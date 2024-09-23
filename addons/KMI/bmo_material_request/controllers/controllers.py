# -*- coding: utf-8 -*-
# from odoo import http


# class BmoMaterialRequest(http.Controller):
#     @http.route('/bmo_material_request/bmo_material_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_material_request/bmo_material_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_material_request.listing', {
#             'root': '/bmo_material_request/bmo_material_request',
#             'objects': http.request.env['bmo_material_request.bmo_material_request'].search([]),
#         })

#     @http.route('/bmo_material_request/bmo_material_request/objects/<model("bmo_material_request.bmo_material_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_material_request.object', {
#             'object': obj
#         })
