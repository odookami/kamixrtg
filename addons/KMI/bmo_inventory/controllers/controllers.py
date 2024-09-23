# -*- coding: utf-8 -*-
# from odoo import http


# class BmoInventory(http.Controller):
#     @http.route('/bmo_inventory/bmo_inventory/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_inventory/bmo_inventory/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_inventory.listing', {
#             'root': '/bmo_inventory/bmo_inventory',
#             'objects': http.request.env['bmo_inventory.bmo_inventory'].search([]),
#         })

#     @http.route('/bmo_inventory/bmo_inventory/objects/<model("bmo_inventory.bmo_inventory"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_inventory.object', {
#             'object': obj
#         })
