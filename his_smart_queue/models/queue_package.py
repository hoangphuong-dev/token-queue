# -*- coding: utf-8 -*-
from odoo import models, fields, _

HIS_HEALTH_CHECK_PACKAGE = 'his.health.check.package'
PRODUCT_PRODUCT = 'product.product'


class QueuePackage(models.Model):
    _description = _('Health Check Package')  # Gói Khám Sức Khỏe
    _inherit = HIS_HEALTH_CHECK_PACKAGE

    code = fields.Char(string=_('Package Code'), required=True)  # Mã Gói
    service_ids = fields.Many2many(PRODUCT_PRODUCT, string=_('Included Services'))  # Dịch Vụ Bao Gồm
    active = fields.Boolean(string=_('Active'), default=True)  # Hoạt Động

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _('Package code must be unique!'))  # Mã gói phải là duy nhất!
    ]
