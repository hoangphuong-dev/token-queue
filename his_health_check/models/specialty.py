# -*- coding: utf-8 -*-
from odoo import fields, models

HR_DEPARTMENT = 'hr.department'
PHYSICIAN_SPECIALTY = 'physician.specialty'


class HisHealthCheckSpecialty(models.Model):
    _inherit = PHYSICIAN_SPECIALTY

    department_ids = fields.One2many(
        comodel_name=HR_DEPARTMENT,
        inverse_name='specialty_id',
        string='Departments',
        help="The departments associated with this health check specialty."
    )
