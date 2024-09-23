# -*- coding: utf-8 -*-
# from odoo import http


# class BmoMrp(http.Controller):
#     @http.route('/bmo_mrp/bmo_mrp/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_mrp/bmo_mrp/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_mrp.listing', {
#             'root': '/bmo_mrp/bmo_mrp',
#             'objects': http.request.env['bmo_mrp.bmo_mrp'].search([]),
#         })

#     @http.route('/bmo_mrp/bmo_mrp/objects/<model("bmo_mrp.bmo_mrp"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_mrp.object', {
#             'object': obj
#         })
