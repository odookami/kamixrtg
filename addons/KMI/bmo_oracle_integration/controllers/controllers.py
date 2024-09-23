# -*- coding: utf-8 -*-
# from odoo import http


# class BmoApi(http.Controller):
#     @http.route('/bmo_api/bmo_api/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_api/bmo_api/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_api.listing', {
#             'root': '/bmo_api/bmo_api',
#             'objects': http.request.env['bmo_api.bmo_api'].search([]),
#         })

#     @http.route('/bmo_api/bmo_api/objects/<model("bmo_api.bmo_api"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_api.object', {
#             'object': obj
#         })
