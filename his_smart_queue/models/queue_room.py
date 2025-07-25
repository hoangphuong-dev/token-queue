# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

HR_DEPARTMENT = 'hr.department'
HIS_QUEUE_TOKEN = "his.queue.token"
PRODUCT_PRODUCT = 'product.product'
HIS_QUEUE_COORDINATION_LOG = 'his.queue.coordination.log'
IR_ACTIONS_WINDOW = "ir.actions.act_window"


class QueueRoom(models.Model):
    _description = _('Service Room')
    _inherit = HR_DEPARTMENT

    code = fields.Char(string=_('Room Code'), required=True)
    service_id = fields.Many2one(PRODUCT_PRODUCT, string=_('Service'), required=True)
    capacity = fields.Integer(string=_('Capacity'), default=1,
                              help=_("Number of patients that can be served simultaneously"))
    current_queue = fields.One2many(HIS_QUEUE_TOKEN, 'room_id', string=_('Current Queue'),
                                    domain=[('state', '=', 'waiting')])
    queue_length = fields.Integer(string=_('Queue Length'), compute='_compute_queue_length')
    estimated_wait_time = fields.Float(string=_('Estimated Wait Time (minutes)'), compute='_compute_wait_time')
    active = fields.Boolean(string=_('Active'), default=True)
    color = fields.Integer(string=_('Color'), default=0)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _('Room code must be unique!'))
    ]

    @api.depends('current_queue')
    def _compute_queue_length(self):
        """Tính toán độ dài hàng đợi hiện tại"""
        for room in self:
            room.queue_length = len(room.current_queue)

    @api.depends('queue_length', 'service_id.average_duration')
    def _compute_wait_time(self):
        """Tính toán thời gian chờ ước tính cho bệnh nhân mới"""
        for room in self:
            avg_duration = room.service_id.average_duration
            # Công thức: Số người đợi * Thời gian trung bình / Công suất phòng
            room.estimated_wait_time = room.queue_length * avg_duration / room.capacity

    def action_view_tokens(self):
        """Xem tất cả token cho phòng này"""
        self.ensure_one()
        return {
            'name': _('Token - %s') % self.name,
            'view_mode': 'list,form',
            'res_model': 'his.queue.token',
            'domain': [('room_id', '=', self.id), ('state', '=', 'waiting')],  # Chỉ lấy token waiting
            'type': IR_ACTIONS_WINDOW,
            'context': {
                'default_room_id': self.id,
                'default_state': 'waiting',
                'search_default_state': 'waiting'  # Thêm filter mặc định
            }
        }

    def action_view_coordination_history(self):
        """Xem lịch sử điều phối của phòng"""
        self.ensure_one()
        return {
            'name': 'Coordination history - %s' % self.name,
            'type': IR_ACTIONS_WINDOW,
            'res_model': HIS_QUEUE_COORDINATION_LOG,
            'view_mode': 'list,form',
            'views': [[False, 'list'], [False, 'form']],
            'domain': [
                '|',
                ('from_room_id', '=', self.id),
                ('to_room_id', '=', self.id)
            ],
            'context': dict(self.env.context,
                            default_room_id=self.id,
                            search_default_room_filter=1,
                            search_default_today=1),
            'target': 'current',
        }
