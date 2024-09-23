# -*- coding: utf-8 -*-
# from odoo import http


# class BmoDumping(http.Controller):
#     @http.route('/bmo_dumping/bmo_dumping/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_dumping/bmo_dumping/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_dumping.listing', {
#             'root': '/bmo_dumping/bmo_dumping',
#             'objects': http.request.env['bmo_dumping.bmo_dumping'].search([]),
#         })

#     @http.route('/bmo_dumping/bmo_dumping/objects/<model("bmo_dumping.bmo_dumping"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_dumping.object', {
#             'object': obj
#         })
