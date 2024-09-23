# -*- coding: utf-8 -*-
# from odoo import http


# class BmoMrpCost(http.Controller):
#     @http.route('/bmo_mrp_cost/bmo_mrp_cost/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_mrp_cost/bmo_mrp_cost/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_mrp_cost.listing', {
#             'root': '/bmo_mrp_cost/bmo_mrp_cost',
#             'objects': http.request.env['bmo_mrp_cost.bmo_mrp_cost'].search([]),
#         })

#     @http.route('/bmo_mrp_cost/bmo_mrp_cost/objects/<model("bmo_mrp_cost.bmo_mrp_cost"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_mrp_cost.object', {
#             'object': obj
#         })
