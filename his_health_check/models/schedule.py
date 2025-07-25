# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

HR_DEPARTMENT = 'hr.department'
PHYSICIAN = 'his.physician'


class HisHealthCheckSchedule(models.Model):
    _name = 'his.health.check.schedule'
    _description = 'Health Check Schedule'

    name = fields.Char(string='Name', compute='_compute_name')
    doctor_id = fields.Many2one(PHYSICIAN, string='Doctor')
    room_id = fields.Many2one(HR_DEPARTMENT, string='Room')
    start_datetime = fields.Datetime(string='Start Datetime', required=True)
    end_datetime = fields.Datetime(string='End Datetime', required=True)

    @api.depends('doctor_id', 'room_id')
    def _compute_name(self):
        """Tự động cập nhật tên lịch dựa trên tên bác sĩ và phòng"""
        for rec in self:
            rec.name = f"{rec.doctor_id.name} - {rec.room_id.name}"

    @api.constrains('start_datetime', 'end_datetime')
    def _check_datetime(self):
        """Đảm bảo thời gian kết thúc không nhỏ hơn thời gian bắt đầu và không được tạo lịch trong quá khứ"""
        for rec in self:
            # Kiểm tra thời gian kết thúc phải >= thời gian bắt đầu
            if rec.end_datetime and rec.start_datetime and rec.end_datetime < rec.start_datetime:
                raise ValidationError(_('End Datetime must be greater than or equal to Start Datetime.'))

            # Kiểm tra không được tạo lịch trong quá khứ
            if rec.start_datetime and rec.start_datetime < fields.Datetime.now():
                raise ValidationError(_('Cannot create schedule in the past. Start Datetime must be in the future.'))
