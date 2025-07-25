# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.exceptions import UserError


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    clinic_medical_event = fields.Text("Medical Event")

    def write(self, values):
        if not self._context.get('clinic_avoid_check'):
            for rec in self:
                if rec.clinic_medical_event and 'videocall_channel_id' not in values:
                    raise UserError(
                        _("Medical operation is linked with this event. Please update data on respective medical record not here."))
        return super().write(values)

    def unlink(self):
        if not self._context.get('clinic_avoid_check'):
            for rec in self:
                if rec.clinic_medical_event:
                    raise UserError(_('There is already linked medical operation with this record.'))
        return super().unlink()
