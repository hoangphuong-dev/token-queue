# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class ClinicHis(http.Controller):

    @http.route(['/mate/data'], type='json', auth="public", methods=['POST'], website=True)
    def clinic_system_data(self, **kw):
        return request.env['res.company'].clinic_get_blocking_data()
