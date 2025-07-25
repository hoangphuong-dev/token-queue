# -*- coding: utf-8 -*-
# Part of Mate See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.service import common
import requests
import json
IR_MODULE_MODULE = 'ir.module.module'
IR_CONFIG_PARAMETER = "ir.config_parameter"
CLINIC_ACCESS_EXPIRED = "clinic.access.expired"


class ResCompany(models.Model):
    _inherit = "res.company"

    birthday_mail_template_id = fields.Many2one('mail.template', 'Birthday Wishes Template',
                                                help="This will set the default mail template for birthday wishes.")
    unique_gov_code = fields.Boolean('Unique Government Identity for Patient',
                                     help='Set this True if the Government Identity in patients should be unique.')

    # Call this method directly in case of dependency issue like clinic_certification (call in his_certification)
    def clinic_create_sequence(self, name, code, prefix, padding=3):
        self.env['ir.sequence'].sudo().create({
            'name': self.name + " : " + name,
            'code': code,
            'padding': padding,
            'number_next': 1,
            'number_increment': 1,
            'prefix': prefix,
            'company_id': self.id,
            'clinic_auto_create': False,
        })

    def clinic_auto_create_sequences(self):
        sequences = self.env['ir.sequence'].search([('clinic_auto_create', '=', True)])
        for sequence in sequences:
            self.clinic_create_sequence(name=sequence.name, code=sequence.code, prefix=sequence.prefix,
                                        padding=sequence.padding)

    # Auto create marked sequences in other HIS modules.
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            record.clinic_auto_create_sequences()
        return res

    @api.model
    def clinic_get_blocking_data(self):
        ir_config_model = self.env[IR_CONFIG_PARAMETER]
        access_is_blocked = ir_config_model.sudo().get_param(CLINIC_ACCESS_EXPIRED, "False")
        message = ''
        if access_is_blocked != 'False':
            message = ir_config_model.sudo().get_param("clinic.access.message")
            if not message:
                message = "Your Access Are blocked please contact at info@mate.com.vn"
        return {"name": message}

    @api.model
    def clinic_send_access_data(self, data):
        ir_config_model = self.env[IR_CONFIG_PARAMETER].sudo()
        try:
            domain = "https://www.mate.com.vn" + '/mate/module/checksubscription'
            reply = requests.post(domain, json.dumps(data),
                                  headers={'accept': 'application/json', 'Content-Type': 'application/json'})
            if reply.status_code == 200:
                reply = json.loads(reply.text)
                subscription_status = reply['result'].get('subscription_status')
                if subscription_status != 'active':
                    ir_config_model.set_param(CLINIC_ACCESS_EXPIRED, "True")
                if subscription_status == 'active':
                    ir_config_model.set_param(CLINIC_ACCESS_EXPIRED, "False")
        except Exception:
            pass

    def _get_base_access_data(self):
        """Thu thập dữ liệu cơ bản của hệ thống"""
        user = self.env.user
        company = user.sudo().company_id
        ir_config_model = self.env[IR_CONFIG_PARAMETER].sudo()
        module = self.env[IR_MODULE_MODULE].sudo()

        data = {
            "installed_modules": module.search([('state', '=', 'installed')]).mapped('name'),
            "db_secret": ir_config_model.get_param("database.secret"),
            "db_uuid": ir_config_model.get_param("database.uuid"),
            "company_name": company.name,
            "email": company.email,
            "country": company.country_id and company.country_id.name or '',
            "mobile": company.mobile,
            "url": ir_config_model.get_param("web.base.url"),
            'users': self.env['res.users'].sudo().search_count([('share', '=', False)]),
            'physicians': self.env['his.physician'].sudo().search_count([]),
            'patients': self.env['his.patient'].sudo().search_count([]),
        }
        return data

    def _add_system_version_data(self, data):
        """Thêm thông tin phiên bản hệ thống"""
        try:
            data['db_name'] = self.env.cr.dbname
            version_info = common.exp_version()
            data['version'] = version_info.get('server_serie')
            data['server_version'] = version_info.get('server_version')
        except Exception:
            pass

    def _add_his_module_data(self, data):
        """Thêm dữ liệu của module HIS chính"""
        module = self.env[IR_MODULE_MODULE].sudo()
        if not module.search([('name', '=', 'his'), ('state', '=', 'installed')]):
            return

        try:
            data.update({
                'appointments': self.env['his.appointment'].sudo().search_count([]),
                'evaluations': self.env['clinic.patient.evaluation'].sudo().search_count([]),
                'prescriptions': self.env['prescription.order'].sudo().search_count([]),
                'procedures': self.env['clinic.patient.procedure'].sudo().search_count([]),
                'treatments': self.env['his.treatment'].sudo().search_count([]),
            })
        except Exception:
            pass

    def _add_optional_module_data(self, data):
        """Thêm dữ liệu từ các module tùy chọn"""
        module = self.env[IR_MODULE_MODULE].sudo()

        # Định nghĩa mapping giữa module và dữ liệu cần thu thập
        module_data_mapping = {
            'his_insurance': {
                'insurance_policies': 'his.patient.insurance',
                'claims': 'his.insurance.claim'
            },
            'his_certification': {
                'certificates': 'certificate.management'
            },
            'his_inpatient_management': {
                'hospitalizations': 'clinic.hospitalization'
            },
            'clinic_printed_form': {
                'consentforms': 'clinic.consent.form'
            },
            'his_laboratory': {
                'laboratory_requests': 'clinic.laboratory.request',
                'laboratory_results': 'patient.laboratory.test'
            },
            'his_radiology': {
                'radiology_requests': 'clinic.radiology.request',
                'radiology_results': 'patient.radiology.test'
            },
            'his_doctor_fee_reimbursement': {
                'commissions': 'clinic.commission'
            },
            'his_vaccination': {
                'vaccinations': 'clinic.vaccination'
            },
            'his_emergency': {
                'emergencies': 'his.emergency'
            },
            'his_surgery': {
                'surgeries': 'his.surgery'
            },
            'clinic_sms': {
                'sms': 'clinic.sms'
            },
            'clinic_whatsapp': {
                'whatsapp': 'clinic.whatsapp.message'
            }
        }

        for module_name, module_data in module_data_mapping.items():
            if module.search([('name', '=', module_name), ('state', '=', 'installed')]):
                self._collect_module_data(data, module_data)

    def _collect_module_data(self, data, module_data):
        """Thu thập dữ liệu từ một module cụ thể"""
        try:
            for key, model_name in module_data.items():
                data[key] = self.env[model_name].sudo().search_count([])
        except Exception:
            pass

    @api.model
    def clinic_update_access_data(self):
        """Cập nhật dữ liệu truy cập - đã được refactor để giảm độ phức tạp"""
        # Thu thập dữ liệu cơ bản
        data = self._get_base_access_data()

        # Thêm thông tin phiên bản
        self._add_system_version_data(data)

        # Thêm dữ liệu từ module HIS chính
        self._add_his_module_data(data)

        # Thêm dữ liệu từ các module tùy chọn
        self._add_optional_module_data(data)

        # Gửi dữ liệu
        self.clinic_send_access_data(data)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    birthday_mail_template_id = fields.Many2one('mail.template',
                                                related='company_id.birthday_mail_template_id',
                                                string='Birthday Wishes Template',
                                                help="This will set the default mail template for birthday wishes.",
                                                readonly=False)
    unique_gov_code = fields.Boolean('Unique Government Identity for Patient',
                                     related='company_id.unique_gov_code', readonly=False,
                                     help='Set this True if the Government Identity in patients should be unique.')
