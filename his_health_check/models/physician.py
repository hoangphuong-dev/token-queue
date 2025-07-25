# -*- coding: utf-8 -*-
from odoo import fields, models, api

PHYSICIAN_SPECIALTY = 'physician.specialty'
HIS_HEALTH_CHECK_PHYSICIAN_ROLE = 'his.health.check.physician.role'


class HisHealthCheckPhysicianRole(models.Model):
    _name = HIS_HEALTH_CHECK_PHYSICIAN_ROLE
    _description = 'Physician Role'

    name = fields.Char(string='Role Name', required=True)
    code = fields.Char(string='Code')


class HisHealthCheckPhysician(models.Model):
    _inherit = 'his.physician'

    specialty_ids = fields.Many2many(
        PHYSICIAN_SPECIALTY, 'physician_specialty_rel', 'physician_id', 'specialty_id', string='Specialties')
    role_ids = fields.Many2many(
        HIS_HEALTH_CHECK_PHYSICIAN_ROLE, 'physician_role_rel', 'physician_id', 'role_id', string='Roles',
        tracking=True)
    role_names = fields.Char(string='Roles', compute='_compute_role_names', store=False)
    specialty_names = fields.Char(string='Specialties', compute='_compute_specialty_names', store=False)
    is_gp = fields.Boolean(compute='_compute_is_gp', store=False)
    is_specialist = fields.Boolean(compute='_compute_is_specialist', store=False)
    schedule_ids = fields.One2many('his.health.check.schedule', 'doctor_id', string='Schedules')

    @api.model_create_multi
    def create(self, vals_list):
        """
        Ghi đè hàm tạo:
        - Gán email làm login nếu có
        - Loại bỏ user_ids nếu có để tránh lỗi kế thừa
        """
        for values in vals_list:
            if values.get('email'):
                values['login'] = values.get('email')
            if values.get('user_ids'):
                values.pop('user_ids')

        res = super(HisHealthCheckPhysician, self).create(vals_list)
        return res

    @api.depends('role_ids.name')
    def _compute_role_names(self):
        """Ghép tên các vai trò của bác sĩ thành chuỗi, cách nhau bởi dấu phẩy"""
        for rec in self:
            rec.role_names = ', '.join(rec.role_ids.mapped('name')) if rec.role_ids else ''

    @api.depends('specialty_ids.name')
    def _compute_specialty_names(self):
        """Ghép tên các chuyên khoa của bác sĩ thành chuỗi, cách nhau bởi dấu phẩy"""
        for rec in self:
            rec.specialty_names = ', '.join(rec.specialty_ids.mapped('name')) if rec.specialty_ids else ''

    @api.depends('role_ids')
    def _compute_is_gp(self):
        """Đánh dấu bác sĩ là GP nếu có vai trò tương ứng"""
        gp_role = self.env.ref('his_health_check.physician_role_gp', raise_if_not_found=False)
        for rec in self:
            rec.is_gp = gp_role in rec.role_ids if gp_role else False

    @api.depends('role_ids')
    def _compute_is_specialist(self):
        """Đánh dấu bác sĩ là Specialist nếu có vai trò tương ứng"""
        specialist_role = self.env.ref('his_health_check.physician_role_specialist', raise_if_not_found=False)
        for rec in self:
            rec.is_specialist = specialist_role in rec.role_ids if specialist_role else False
