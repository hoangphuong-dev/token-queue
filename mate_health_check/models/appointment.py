# -*- coding: utf-8 -*-
from odoo import models, api, fields
from odoo.exceptions import UserError
from odoo import _
import logging

_logger = logging.getLogger(__name__)

HIS_PATIENT = 'his.patient'
HIS_APPOINTMENT = 'his.appointment'
MATE_HEALTH_CHECK_PACKAGE_LINE = 'mate.health.check.package.line'
MATE_HEALTH_CHECK_PACKAGE = 'mate.health.check.package'


class MateAppointment(models.Model):
    _name = HIS_APPOINTMENT
    _description = 'Mate Appointment'

    patient_id = fields.Many2one(HIS_PATIENT, string='Patient', required=True, ondelete='restrict', auto_join=True)

    # Thêm các trường related dựa trên view
    name = fields.Char(related='patient_id.name', string='Patient', readonly=True, store=True)
    patient_id_number = fields.Char(related='patient_id.patient_id_number', string='PID', readonly=True, store=True)
    gender = fields.Selection(related='patient_id.gender', string='Gender', readonly=True, store=True)
    date_of_birth = fields.Date(related='patient_id.date_of_birth', string='Date of Birth', readonly=True, store=True)
    image_1920 = fields.Binary(related='patient_id.image_1920', string='Image', readonly=True)
    age = fields.Integer(related='patient_id.age', string='Age', readonly=True, store=True)
    priority_level = fields.Many2one(related='patient_id.priority_level', string='Priority Levels', readonly=True,
                                     store=True)
    insurance_code = fields.Char(related='patient_id.insurance_code', string='Insurance Code', readonly=True,
                                 store=True)
    street = fields.Char(related='patient_id.street', string='Address', readonly=True)
    nationality_id = fields.Many2one(related='patient_id.nationality_id', string='Nationality', readonly=True)
    nation = fields.Char(related='patient_id.nation', string='Nation', readonly=True)
    phone = fields.Char(related='patient_id.phone', string='Phone', readonly=True)
    email = fields.Char(related='patient_id.email', string='Email', readonly=True)

    # Các trường của appointment
    package_id = fields.Many2one(
        MATE_HEALTH_CHECK_PACKAGE,
        string='Package',
        required=True,
        help='Package assigned to the patient for health checks'
    )
    package_line_ids = fields.One2many(
        comodel_name=MATE_HEALTH_CHECK_PACKAGE_LINE,
        compute='_compute_package_line_ids',
        string='Package Lines',
        readonly=True
    )
    expected_date = fields.Datetime(string='Expected Date')
    real_date = fields.Datetime(string='Real Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('cancel', 'Cancelled'),
        ('done', 'Done'),
    ], string='Status', default='draft')

    # Dịch vụ bổ sung
    addon_service_line_ids = fields.One2many(
        MATE_HEALTH_CHECK_PACKAGE_LINE,
        'appointment_id',
        string='Dịch vụ bổ sung',
        domain=[('package_id', '=', False)]
    )

    @api.depends('package_id.package_line_ids')
    def _compute_package_line_ids(self):
        """Lấy danh sách các package lines từ package"""
        for rec in self:
            if rec.package_id:
                rec.package_line_ids = rec.package_id.package_line_ids
            else:
                rec.package_line_ids = self.env[MATE_HEALTH_CHECK_PACKAGE_LINE]

    @api.constrains('package_id')
    def _check_package_id(self):
        """Kiểm tra package_id không được để trống"""
        for rec in self:
            if not rec.package_id:
                raise UserError(_('package is required field.'))

    def action_appointment_create(self):
        for rec in self:
            rec.state = 'confirm'

    def action_appointment_confirm(self):
        for rec in self:
            rec.state = 'waiting'
            # Tạo token cho bước khám bệnh đầu tiên
            rec._create_first_examination_token()

    def action_appointment_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def _create_first_examination_token(self):
        """Tạo token cho bước khám bệnh đầu tiên trong gói của bệnh nhân"""
        self.ensure_one()

        # Lấy module queue token
        queue_token = self.env['mate.queue.token']
        package = self.package_id

        # Lấy nhóm dịch vụ đầu tiên trong gói khám dựa vào MATE_HEALTH_CHECK_PACKAGE_GROUP_ORDER
        first_group_order = self.env['mate.health.check.package.group.order'].search([
            ('package_id', '=', package.id)
        ], order='sequence asc', limit=1)

        if not first_group_order:
            raise UserError(
                _('The %s examination package does not have a service group order configured') % package.name)

        first_group = first_group_order.group_id

        if not first_group:
            raise UserError(_('First service group in package not found'))

        # Lấy dịch vụ đầu tiên của nhóm dựa vào các thông tin của bệnh nhân
        if not first_group.service_ids:
            raise UserError(_('Service group %s has no services') % first_group.name)

        # Lấy dịch vụ đầu tiên trong nhóm
        first_service = first_group.service_ids[0]

        # Tạo token cho dịch vụ đầu tiên
        token_vals = {
            'patient_id': self.patient_id.id,
            'service_id': first_service.id,
            'service_group_id': first_group.id,
            'package_id': package.id,
            'priority': 0,
            'state': 'waiting',
            'notes': _('Token generated from appointment confirmation - First step: %s') % first_service.name,
        }

        token = queue_token.create(token_vals)

        # Cập nhật thông tin bệnh nhân để liên kết với queue system
        self.patient_id.write({
            'queue_package_id': package.id,
            'current_service_group_id': first_group.id,
            'current_waiting_token_id': token.id,
        })

        _logger.info(
            "Đã tạo token đầu tiên cho bệnh nhân %s: Token %s cho dịch vụ %s trong nhóm %s của gói %s",
            self.patient_id.name, token.name, first_service.name, first_group.name, package.name
        )

        return token
