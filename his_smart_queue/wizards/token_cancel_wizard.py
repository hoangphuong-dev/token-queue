# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TokenCancelWizard(models.TransientModel):
    _name = 'his.queue.token.cancel.wizard'
    _description = 'Token Cancellation Wizard'

    token_id = fields.Many2one('his.queue.token', string='Token', required=True)
    cancellation_reason = fields.Selection([
        ('patient_refused', 'Bệnh nhân yêu cầu dừng khám'),
        ('beyond_expertise', 'Tình trạng bệnh lý vượt quá chuyên môn'),
        ('ineligible_condition', 'Bệnh nhân không đáp ứng điều kiện khám'),
        ('emergency_isolation', 'Bệnh nhân trong tình trạng nguy hiểm hoặc có yếu tố cách ly'),
        ('other', 'Lý do khác'),
    ], string='Lý do từ chối', required=True, default='patient_refused')

    custom_reason = fields.Text(string='Lý do cụ thể', placeholder='Nhập lý do từ chối cụ thể...')

    @api.onchange('cancellation_reason')
    def _onchange_cancellation_reason(self):
        """Clear custom reason if not 'other'"""
        if self.cancellation_reason != 'other':
            self.custom_reason = False

    def action_confirm_cancel(self):
        """Confirm cancellation with reason"""
        if not self.token_id:
            raise UserError(_("Token không tồn tại"))

        if self.token_id.state in ['completed', 'cancelled']:
            raise UserError(_("cannot_cancel_completed_or_cancelled_token"))

        reason_text = dict(self._fields['cancellation_reason'].selection)[self.cancellation_reason]

        cancellation_notes = f"Lý do từ chối: {reason_text}"

        if self.cancellation_reason == 'other' and self.custom_reason:
            cancellation_notes += f"\nLý do cụ thể: {self.custom_reason}"
        elif self.custom_reason:
            cancellation_notes += f"\nChi tiết: {self.custom_reason}"

        # Add timestamp
        cancellation_notes += f"\nThời gian từ chối: {fields.Datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

        # Combine with existing notes if any
        existing_notes = self.token_id.notes or ""
        if existing_notes:
            final_notes = f"{existing_notes}\n\n--- TỪCHỐI KHÁM ---\n{cancellation_notes}"
        else:
            final_notes = f"--- TỪCHỐI KHÁM ---\n{cancellation_notes}"

        # Update token
        self.token_id.write({
            'state': 'cancelled',
            'notes': final_notes
        })

        # Re-sort queue
        self.token_id._add_to_queue_and_sort()

        return {'type': 'ir.actions.act_window_close'}
