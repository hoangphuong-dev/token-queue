# -*- coding: utf-8 -*-

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def clinic_action_assign(self):
        self._action_assign()

    def clinic_action_done(self):
        self.picked = True
        self._action_done()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
