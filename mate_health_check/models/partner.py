# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date


class ResPartner(models.Model):
    _inherit = "res.partner"
    name = fields.Char(tracking=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')], string='Gender', default='male', tracking=True)
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    age = fields.Integer(string='Age', compute='_compute_age')

    @api.depends('date_of_birth')
    def _compute_age(self):
        """Tính tuổi từ ngày sinh"""
        for patient in self:
            if patient.date_of_birth:
                today = date.today()
                born = patient.date_of_birth
                patient.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                patient.age = 0

# Hàm này dùng để tạo mới một bản ghi bệnh nhân (his.patient) từ đối tượng partner hiện tại
    def create_patient(self):
        self.ensure_one()
        patient_id = self.env['his.patient'].create({
            'partner_id': self.id,
            'name': self.name,
        })
        return patient_id
