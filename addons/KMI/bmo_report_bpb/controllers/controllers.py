# -*- coding: utf-8 -*-
# from odoo import http


# class BmoReportBpb(http.Controller):
#     @http.route('/bmo_report_bpb/bmo_report_bpb/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_report_bpb/bmo_report_bpb/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_report_bpb.listing', {
#             'root': '/bmo_report_bpb/bmo_report_bpb',
#             'objects': http.request.env['bmo_report_bpb.bmo_report_bpb'].search([]),
#         })

#     @http.route('/bmo_report_bpb/bmo_report_bpb/objects/<model("bmo_report_bpb.bmo_report_bpb"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_report_bpb.object', {
#             'object': obj
#         })
