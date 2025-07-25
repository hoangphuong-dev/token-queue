# -*- coding: utf-8 -*-

from odoo import fields, models


class ResourceCalendar(models.Model):
    _description = "Working Schedule"
    _name = "resource.calendar"
    _inherit = ['resource.calendar', 'his.mixin']

    category = fields.Selection([('doctor', 'Doctor'), ('nurse', 'Nurse')], string='Category')
    department_id = fields.Many2one('hr.department', ondelete='restrict',
                                    domain=lambda self: self.clinic_get_department_domain(),
                                    string='Department', help="Department for which the schedule is applicable.")
    physician_ids = fields.Many2many('his.physician', 'physician_resource_rel', 'physician_id', 'resource_id',
                                     'Physicians')
