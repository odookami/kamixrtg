# -*- coding: utf-8 -*-
# from odoo import http


# class BmoVolumeNutrive(http.Controller):
#     @http.route('/bmo_volume_nutrive/bmo_volume_nutrive/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_volume_nutrive/bmo_volume_nutrive/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_volume_nutrive.listing', {
#             'root': '/bmo_volume_nutrive/bmo_volume_nutrive',
#             'objects': http.request.env['bmo_volume_nutrive.bmo_volume_nutrive'].search([]),
#         })

#     @http.route('/bmo_volume_nutrive/bmo_volume_nutrive/objects/<model("bmo_volume_nutrive.bmo_volume_nutrive"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_volume_nutrive.object', {
#             'object': obj
#         })
