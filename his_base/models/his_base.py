# -*- coding: utf-8 -*-

from odoo import fields, models


class MatePatientTag(models.Model):
    _name = "his.patient.tag"
    _description = "Clinic Patient Tag"

    def _get_default_color(self):
        return 1 + (self.env.uid % 11)

    name = fields.Char(string="Name")
    color = fields.Integer('Color', default=_get_default_color)


class MateTherapeuticEffect(models.Model):
    _name = "his.therapeutic.effect"
    _description = "Clinic Therapeutic Effect"

    code = fields.Char(string="Code")
    name = fields.Char(string="Name", required=True)


class MateReligion(models.Model):
    _name = 'clinic.religion'
    _description = "Clinic Religion"

    name = fields.Char(string="Name", required=True, translate=True)
    code = fields.Char(string='code')
    notes = fields.Char(string='Notes')

    _sql_constraints = [('name_uniq', 'UNIQUE(name)', 'Name must be unique!')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
