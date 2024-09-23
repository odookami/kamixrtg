# -*- coding: utf-8 -*-
# from odoo import http


# class BmoInventoryQc(http.Controller):
#     @http.route('/bmo_inventory_qc/bmo_inventory_qc/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_inventory_qc/bmo_inventory_qc/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_inventory_qc.listing', {
#             'root': '/bmo_inventory_qc/bmo_inventory_qc',
#             'objects': http.request.env['bmo_inventory_qc.bmo_inventory_qc'].search([]),
#         })

#     @http.route('/bmo_inventory_qc/bmo_inventory_qc/objects/<model("bmo_inventory_qc.bmo_inventory_qc"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_inventory_qc.object', {
#             'object': obj
#         })
