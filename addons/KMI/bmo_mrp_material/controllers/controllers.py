# -*- coding: utf-8 -*-
# from odoo import http


# class BmoMaterialUsage(http.Controller):
#     @http.route('/bmo_material_usage/bmo_material_usage/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_material_usage/bmo_material_usage/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_material_usage.listing', {
#             'root': '/bmo_material_usage/bmo_material_usage',
#             'objects': http.request.env['bmo_material_usage.bmo_material_usage'].search([]),
#         })

#     @http.route('/bmo_material_usage/bmo_material_usage/objects/<model("bmo_material_usage.bmo_material_usage"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_material_usage.object', {
#             'object': obj
#         })
