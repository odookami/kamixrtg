# -*- coding: utf-8 -*-
# from odoo import http


# class BmoPacking(http.Controller):
#     @http.route('/bmo_packing/bmo_packing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_packing/bmo_packing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_packing.listing', {
#             'root': '/bmo_packing/bmo_packing',
#             'objects': http.request.env['bmo_packing.bmo_packing'].search([]),
#         })

#     @http.route('/bmo_packing/bmo_packing/objects/<model("bmo_packing.bmo_packing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_packing.object', {
#             'object': obj
#         })
