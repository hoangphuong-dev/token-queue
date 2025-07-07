# -*- coding: utf-8 -*-
# Part of Mate See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.service import common
import requests
import json


class ResCompany(models.Model):
    _inherit = "res.company"

    birthday_mail_template_id = fields.Many2one('mail.template', 'Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.")
    unique_gov_code = fields.Boolean('Unique Government Identity for Patient', help='Set this True if the Government Identity in patients should be unique.')

    #Call this method directly in case of dependency issue like clinic_certification (call in his_certification)
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
        sequences = self.env['ir.sequence'].search([('clinic_auto_create','=',True)])
        for sequence in sequences:
            self.clinic_create_sequence(name=sequence.name, code=sequence.code, prefix=sequence.prefix, padding=sequence.padding)

    #Auto create marked sequences in other HIS modules.
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            record.clinic_auto_create_sequences()
        return res

    @api.model
    def clinic_get_blocking_data(self):
        ir_config_model = self.env["ir.config_parameter"]
        access_is_blocked = ir_config_model.sudo().get_param("clinic.access.expired","False")
        message = ''
        if access_is_blocked!='False':
            message = ir_config_model.sudo().get_param("clinic.access.message")
            if not message:
                message = "Your Access Are blocked please contact at info@mate.com.vn"
        return {"name": message}

    @api.model
    def clinic_send_access_data(self, data):
        ir_config_model = self.env["ir.config_parameter"].sudo()
        try:
            domain = "https://www.mate.com.vn" + '/mate/module/checksubscription'
            reply = requests.post(domain, json.dumps(data), headers={'accept': 'application/json', 'Content-Type': 'application/json'})
            if reply.status_code==200:
                reply = json.loads(reply.text)
                subscription_status = reply['result'].get('subscription_status')
                if subscription_status!='active':
                    ir_config_model.set_param("clinic.access.expired", "True")
                if subscription_status=='active':
                    ir_config_model.set_param("clinic.access.expired", "False")
        except:
            pass

    @api.model
    def clinic_update_access_data(self):
        user = self.env.user
        company = user.sudo().company_id
        ir_config_model = self.env["ir.config_parameter"].sudo()        
        Module = self.env['ir.module.module'].sudo()
        data = {
            "installed_modules": Module.search([('state','=','installed')]).mapped('name'), 
            "db_secret": ir_config_model.get_param("database.secret"), 
            "db_uuid": ir_config_model.get_param("database.uuid"),
            "company_name": company.name,
            "email": company.email,
            "country": company.country_id and company.country_id.name or '',
            "mobile": company.mobile,
            "url": ir_config_model.get_param("web.base.url"),
            'users': self.env['res.users'].sudo().search_count([('share','=',False)]),
            'physicians': self.env['his.physician'].sudo().search_count([]),
            'patients': self.env['his.patient'].sudo().search_count([]),
        }

        try:
            data['db_name'] = self.env.cr.dbname
            version_info = common.exp_version()
            data['version'] = version_info.get('server_serie')
            data['server_version'] = version_info.get('server_version')
        except:
            pass

        try:
            if Module.search([('name','=','his'),('state','=','installed')]):
                data.update({
                    'appointments': self.env['his.appointment'].sudo().search_count([]),
                    'evaluations': self.env['clinic.patient.evaluation'].sudo().search_count([]),
                    'prescriptions': self.env['prescription.order'].sudo().search_count([]),
                    'procedures': self.env['clinic.patient.procedure'].sudo().search_count([]),
                    'treatments': self.env['his.treatment'].sudo().search_count([]),
                })
        except:
            pass

        try:
            if Module.search([('name','=','his_insurance'),('state','=','installed')]):
                data['insurance_policies'] = self.env['his.patient.insurance'].sudo().search_count([])
                data['claims'] = self.env['his.insurance.claim'].sudo().search_count([])
            if Module.search([('name','=','his_certification'),('state','=','installed')]):
                data['certificates'] = self.env['certificate.management'].sudo().search_count([])
            if Module.search([('name','=','his_inpatient_management'),('state','=','installed')]):
                data['hospitalizations'] = self.env['clinic.hospitalization'].sudo().search_count([])
            if Module.search([('name','=','clinic_printed_form'),('state','=','installed')]):
                data['consentforms'] = self.env['clinic.consent.form'].sudo().search_count([])
            if Module.search([('name','=','his_laboratory'),('state','=','installed')]):
                data['laboratory_requests'] = self.env['clinic.laboratory.request'].sudo().search_count([])
                data['laboratory_results'] = self.env['patient.laboratory.test'].sudo().search_count([])
            if Module.search([('name','=','his_radiology'),('state','=','installed')]):
                data['radiology_requests'] = self.env['clinic.radiology.request'].sudo().search_count([])
                data['radiology_results'] = self.env['patient.radiology.test'].sudo().search_count([])
            if Module.search([('name','=','his_doctor_fee_reimbursement'),('state','=','installed')]):
                data['commissions'] = self.env['clinic.commission'].sudo().search_count([])
            if Module.search([('name','=','his_vaccination'),('state','=','installed')]):
                data['vaccinations'] = self.env['clinic.vaccination'].sudo().search_count([])
            if Module.search([('name','=','his_emergency'),('state','=','installed')]):
                data['emergencies'] = self.env['his.emergency'].sudo().search_count([])
            if Module.search([('name','=','his_surgery'),('state','=','installed')]):
                data['surgeries'] = self.env['his.surgery'].sudo().search_count([])
            if Module.search([('name','=','clinic_sms'),('state','=','installed')]):
                data['sms'] = self.env['clinic.sms'].sudo().search_count([])
            if Module.search([('name','=','clinic_whatsapp'),('state','=','installed')]):
                data['whatsapp'] = self.env['clinic.whatsapp.message'].sudo().search_count([])
        except:
            pass
        self.clinic_send_access_data(data)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    birthday_mail_template_id = fields.Many2one('mail.template', 
        related='company_id.birthday_mail_template_id',
        string='Birthday Wishes Template',
        help="This will set the default mail template for birthday wishes.", readonly=False)
    unique_gov_code = fields.Boolean('Unique Government Identity for Patient',
         related='company_id.unique_gov_code', readonly=False,
         help='Set this True if the Government Identity in patients should be unique.')