# -*- coding: utf-8 -*-
# from odoo import http


# class BmoLoader(http.Controller):
#     @http.route('/bmo_loader/bmo_loader/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_loader/bmo_loader/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_loader.listing', {
#             'root': '/bmo_loader/bmo_loader',
#             'objects': http.request.env['bmo_loader.bmo_loader'].search([]),
#         })

#     @http.route('/bmo_loader/bmo_loader/objects/<model("bmo_loader.bmo_loader"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_loader.object', {
#             'object': obj
#         })
