# -*- coding: utf-8 -*-
# from odoo import http


# class BmoVerifikasiBerat(http.Controller):
#     @http.route('/bmo_verifikasi_berat/bmo_verifikasi_berat/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_verifikasi_berat/bmo_verifikasi_berat/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_verifikasi_berat.listing', {
#             'root': '/bmo_verifikasi_berat/bmo_verifikasi_berat',
#             'objects': http.request.env['bmo_verifikasi_berat.bmo_verifikasi_berat'].search([]),
#         })

#     @http.route('/bmo_verifikasi_berat/bmo_verifikasi_berat/objects/<model("bmo_verifikasi_berat.bmo_verifikasi_berat"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_verifikasi_berat.object', {
#             'object': obj
#         })
