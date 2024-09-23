# -*- coding: utf-8 -*-
# from odoo import http


# class BmoMrpQc(http.Controller):
#     @http.route('/bmo_mrp_qc/bmo_mrp_qc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_mrp_qc/bmo_mrp_qc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_mrp_qc.listing', {
#             'root': '/bmo_mrp_qc/bmo_mrp_qc',
#             'objects': http.request.env['bmo_mrp_qc.bmo_mrp_qc'].search([]),
#         })

#     @http.route('/bmo_mrp_qc/bmo_mrp_qc/objects/<model("bmo_mrp_qc.bmo_mrp_qc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_mrp_qc.object', {
#             'object': obj
#         })
