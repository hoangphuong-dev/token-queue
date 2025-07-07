# -*- coding: utf-8 -*-
from odoo import fields, models

# Định nghĩa các hằng số tên model để tái sử dụng
RES_PARTNER = 'res.partner'  # Model đối tác (partner) chuẩn của Odoo
HIS_PATIENT = 'his.patient'  # Model bệnh nhân
MATE_HEALTH_CHECK_CUSTOMER_TYPE = 'mate.health.check.customer.type'  # Loại khách hàng


class MateHealthCheckPatient(models.Model):
    _name = HIS_PATIENT  # Tên model trong Odoo
    _description = 'Health Check Patient'  # Mô tả model
    _inherits = {
        RES_PARTNER: 'partner_id',  # Kế thừa các trường của res.partner qua partner_id
    }

    # Trường liên kết với res.partner, bắt buộc phải có
    partner_id = fields.Many2one(RES_PARTNER, required=True, ondelete='restrict', auto_join=True,
                                 string='Related Partner', help='Partner-related data of the Patient')
    active = fields.Boolean(string="Active", default=True)  # Trạng thái hoạt động của bệnh nhân
    priority_level = fields.Many2one(
        MATE_HEALTH_CHECK_CUSTOMER_TYPE,
        string='Priority Levels',
        help='Priority levels assigned to the patient for health checks'  # Mức độ ưu tiên của bệnh nhân
    )
    patient_id_number = fields.Char(string='PID', help='Patient ID', required=True)  # Mã số bệnh nhân (bắt buộc)
    nation = fields.Char(string='Nation')  # Dân tộc
    nationality_id = fields.Many2one("res.country", string="Nationality")  # Quốc tịch
    insurance_code = fields.Char(string='Insurance Code', help='Insurance code of the patient')  # Mã bảo hiểm

    _sql_constraints = [
        ('unique_patient_id_number', 'unique(patient_id_number)', 'Patient ID already exists!')
    ]

    def action_open_smart_queue_view(self):
        """Mở view danh sách bệnh nhân từ module mate_smart_queue nếu có, nếu không thì mở view mặc định"""
        try:
            # Thử tìm action từ module mate_smart_queue
            action = self.env.ref('mate_smart_queue.action_patient_list_main')
            return action.read()[0]
        except ValueError:
            # Nếu không tìm thấy (module mate_smart_queue chưa cài), dùng view mặc định
            return {
                'type': 'ir.actions.act_window',
                'name': 'Patient List',
                'res_model': HIS_PATIENT,
                'view_mode': 'list,form',
                'target': 'current',
            }

    def action_open_queue_list_view(self):
        """Mở view danh sách xếp hàng từ module mate_smart_queue nếu có, nếu không thì mở view mặc định"""
        try:
            # Thử tìm action từ module mate_smart_queue
            action = self.env.ref('mate_smart_queue.action_queue_token')
            return action.read()[0]
        except ValueError:
            # Nếu không tìm thấy (module mate_smart_queue chưa cài), dùng view mặc định
            return {
                'type': 'ir.actions.act_window',
                'name': 'Queue List',
                'res_model': HIS_PATIENT,
                'view_mode': 'list,form',
                'target': 'current',
            }
