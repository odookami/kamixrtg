# -*- coding: utf-8 -*-
# from odoo import http


# class BmoVisualProduk(http.Controller):
#     @http.route('/bmo_visual_produk/bmo_visual_produk/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_visual_produk/bmo_visual_produk/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_visual_produk.listing', {
#             'root': '/bmo_visual_produk/bmo_visual_produk',
#             'objects': http.request.env['bmo_visual_produk.bmo_visual_produk'].search([]),
#         })

#     @http.route('/bmo_visual_produk/bmo_visual_produk/objects/<model("bmo_visual_produk.bmo_visual_produk"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_visual_produk.object', {
#             'object': obj
#         })
