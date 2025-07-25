# coding: utf-8

from odoo import models, fields


class ClinicRescheduleAppointments(models.TransientModel):
    _name = 'clinic.reschedule.appointments'
    _description = "Reschedule Appointments"

    clinic_reschedule_time = fields.Float(string="Reschedule Selected Appointments by (Hours)", required=True)

    def clinic_reschedule_appointments(self):
        appointments = self.env['his.appointment'].search([('id', 'in', self.env.context.get('active_ids'))])
        # Mate: do it in method only to use that method for notifications.
        appointments.clinic_reschedule_appointments(self.clinic_reschedule_time)
