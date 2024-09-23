# -*- coding: utf-8 -*-
# from odoo import http


# class BmoVolumeChilgo(http.Controller):
#     @http.route('/bmo_volume_chilgo/bmo_volume_chilgo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_volume_chilgo/bmo_volume_chilgo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_volume_chilgo.listing', {
#             'root': '/bmo_volume_chilgo/bmo_volume_chilgo',
#             'objects': http.request.env['bmo_volume_chilgo.bmo_volume_chilgo'].search([]),
#         })

#     @http.route('/bmo_volume_chilgo/bmo_volume_chilgo/objects/<model("bmo_volume_chilgo.bmo_volume_chilgo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_volume_chilgo.object', {
#             'object': obj
#         })
