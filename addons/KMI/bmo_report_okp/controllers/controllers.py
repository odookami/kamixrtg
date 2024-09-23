# -*- coding: utf-8 -*-
# from odoo import http


# class BmoReportOkp(http.Controller):
#     @http.route('/bmo_report_okp/bmo_report_okp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_report_okp/bmo_report_okp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_report_okp.listing', {
#             'root': '/bmo_report_okp/bmo_report_okp',
#             'objects': http.request.env['bmo_report_okp.bmo_report_okp'].search([]),
#         })

#     @http.route('/bmo_report_okp/bmo_report_okp/objects/<model("bmo_report_okp.bmo_report_okp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_report_okp.object', {
#             'object': obj
#         })
