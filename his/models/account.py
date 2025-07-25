# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    ref_physician_id = fields.Many2one('res.partner', ondelete='restrict', string='Referring Physician',
                                       index=True, help='Referring Physician')
    appointment_id = fields.Many2one('his.appointment', string='Appointment')
    procedure_id = fields.Many2one('clinic.patient.procedure', string='Patient Procedure')
    hospital_invoice_type = fields.Selection(
        selection_add=[('appointment', 'Appointment'), ('treatment', 'Treatment'), ('procedure', 'Procedure')])
