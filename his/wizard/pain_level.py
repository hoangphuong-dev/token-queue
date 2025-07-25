# coding: utf-8

from odoo import models, fields


class ClinicPainLevel(models.TransientModel):
    _name = 'clinic.pain.level'
    _description = "Pain Level Diagram"

    name = fields.Char()
