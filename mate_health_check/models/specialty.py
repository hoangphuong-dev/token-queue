# -*- coding: utf-8 -*-
from odoo import fields, models

HR_DEPARTMENT = 'hr.department'
PHYSICIAN_SPECIALTY = 'physician.specialty'


class MateHealthCheckSpecialty(models.Model):
    _name = PHYSICIAN_SPECIALTY
    _description = 'Health Check Specialty'
    _order = 'name'

    name = fields.Char(string='Name', required=True)
    department_ids = fields.One2many(
        comodel_name=HR_DEPARTMENT,
        inverse_name='specialty_id',
        string='Departments',
        help="The departments associated with this health check specialty."
    )
