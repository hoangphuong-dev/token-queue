# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class MateHis(http.Controller):

    @http.route(['/validate/prescriptionorder/<prescription_unique_code>'], type='http', auth="public", website=True,
                sitemap=False)
    def prescription_details(self, prescription_unique_code, **post):
        if prescription_unique_code:
            prescription = request.env['prescription.order'].sudo().search(
                [('unique_code', '=', prescription_unique_code)], limit=1)
            if prescription:
                return request.render("his.clinic_prescription_details", {'prescription': prescription})
        return request.render("his.clinic_no_details")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
