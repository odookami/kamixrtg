# -*- coding: utf-8 -*-
# from odoo import http


# class BmoProsesProduksi(http.Controller):
#     @http.route('/bmo_proses_produksi/bmo_proses_produksi/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_proses_produksi/bmo_proses_produksi/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_proses_produksi.listing', {
#             'root': '/bmo_proses_produksi/bmo_proses_produksi',
#             'objects': http.request.env['bmo_proses_produksi.bmo_proses_produksi'].search([]),
#         })

#     @http.route('/bmo_proses_produksi/bmo_proses_produksi/objects/<model("bmo_proses_produksi.bmo_proses_produksi"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_proses_produksi.object', {
#             'object': obj
#         })
