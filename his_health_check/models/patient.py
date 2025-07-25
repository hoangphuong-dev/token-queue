# -*- coding: utf-8 -*-
from odoo import fields, models

RES_PARTNER = 'res.partner'  # Model đối tác (partner) chuẩn của Odoo
HIS_PATIENT = 'his.patient'  # Model bệnh nhân
HIS_HEALTH_CHECK_CUSTOMER_TYPE = 'his.health.check.customer.type'  # Loại khách hàng


class HisHealthCheckPatient(models.Model):
    _inherit = 'his.patient'

    priority_level = fields.Many2one(
        HIS_HEALTH_CHECK_CUSTOMER_TYPE,
        string='Priority Levels',
        help='Priority levels assigned to the patient for health checks'  # Mức độ ưu tiên của bệnh nhân
    )
    code = fields.Char(string='PID', help='Patient ID', required=True)  # Mã số bệnh nhân (bắt buộc)
    insurance_code = fields.Char(string='Insurance Code', help='Insurance code of the patient')  # Mã bảo hiểm

    def action_open_smart_queue_view(self):
        """Mở view danh sách bệnh nhân từ module his_smart_queue nếu có, nếu không thì mở view mặc định"""
        try:
            # Thử tìm action từ module his_smart_queue
            action = self.env.ref('his_smart_queue.action_patient_list_main')
            return action.read()[0]
        except ValueError:
            # Nếu không tìm thấy (module his_smart_queue chưa cài), dùng view mặc định
            return {
                'type': 'ir.actions.act_window',
                'name': 'Patient List',
                'res_model': HIS_PATIENT,
                'view_mode': 'list,form',
                'target': 'current',
            }

    def action_open_queue_list_view(self):
        """Mở view danh sách xếp hàng từ module his_smart_queue nếu có, nếu không thì mở view mặc định"""
        try:
            # Thử tìm action từ module his_smart_queue
            action = self.env.ref('his_smart_queue.action_queue_token')
            return action.read()[0]
        except ValueError:
            # Nếu không tìm thấy (module his_smart_queue chưa cài), dùng view mặc định
            return {
                'type': 'ir.actions.act_window',
                'name': 'Queue List',
                'res_model': HIS_PATIENT,
                'view_mode': 'list,form',
                'target': 'current',
            }
