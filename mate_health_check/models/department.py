# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError

HR_DEPARTMENT = 'hr.department'
PHYSICIAN_SPECIALTY = 'physician.specialty'


class MateHealthCheckDepartment(models.Model):
    _name = HR_DEPARTMENT
    _description = 'Health Check Department'

    name = fields.Char(string='Name', required=True, tracking=True)
    location = fields.Text(
        string='Location',
        help="The physical location of the department."
    )
    capacity = fields.Integer(
        string='Capacity',
        help="The maximum number of patients that can be accommodated in this department."
    )
    specialty_id = fields.Many2one(
        PHYSICIAN_SPECIALTY,
        string='Specialty',
        help="The specialty associated with this department."
    )
    code = fields.Char(
        string='Code',
        help="A unique code for the department, used for identification.",
        required=True
    )
    state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed'),
    ], string='Status', default='open')

    _sql_constraints = [
        ('code_uniq', 'UNIQUE(code)', 'The code must be unique for each department.')
    ]

    def action_open_department_list_view(self):
        """Mở view từ module mate_smart_queue"""
        try:
            # Thử tìm action từ module con
            action = self.env.ref('mate_smart_queue.action_queue_room')
            return action.read()[0]
        except ValueError:
            # Nếu không tìm thấy (module con chưa cài), dùng view mặc định
            return {
                'type': 'ir.actions.act_window',
                'name': 'Department List',
                'res_model': HR_DEPARTMENT,
                'view_mode': 'list,form',
                'target': 'current',
            }

    def action_open_room(self):
        """Mở phòng cho phục vụ"""
        for room in self:
            room.state = 'open'

    def action_close_room(self):
        """Đóng phòng với kiểm tra bệnh nhân"""
        for room in self:
            # Kiểm tra xem có bệnh nhân đang chờ hoặc đang phục vụ trong phòng không
            waiting_patients = self.env['mate.queue.token'].search_count([
                ('room_id', '=', room.id),
                ('state', 'in', ['waiting', 'in_progress'])
            ])
            if waiting_patients > 0:
                raise UserError(_('Cannot close room because there are %d patients waiting or being served.') % waiting_patients)
            else:
                room.state = 'closed'

    def toggle_room_state(self):
        """Đảo trạng thái phòng giữa 'open' (mở) và 'closed' (đóng)"""
        for room in self:
            if room.state == 'open':
                room.action_close_room()
            else:
                room.action_open_room()
