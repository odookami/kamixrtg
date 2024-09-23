# -*- coding: utf-8 -*-
# from odoo import http


# class BmoVolumeHic(http.Controller):
#     @http.route('/bmo_volume_hic/bmo_volume_hic/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_volume_hic/bmo_volume_hic/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_volume_hic.listing', {
#             'root': '/bmo_volume_hic/bmo_volume_hic',
#             'objects': http.request.env['bmo_volume_hic.bmo_volume_hic'].search([]),
#         })

#     @http.route('/bmo_volume_hic/bmo_volume_hic/objects/<model("bmo_volume_hic.bmo_volume_hic"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_volume_hic.object', {
#             'object': obj
#         })
