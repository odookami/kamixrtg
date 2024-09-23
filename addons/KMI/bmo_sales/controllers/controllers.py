# -*- coding: utf-8 -*-
# from odoo import http


# class BmoSales(http.Controller):
#     @http.route('/bmo_sales/bmo_sales/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_sales/bmo_sales/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_sales.listing', {
#             'root': '/bmo_sales/bmo_sales',
#             'objects': http.request.env['bmo_sales.bmo_sales'].search([]),
#         })

#     @http.route('/bmo_sales/bmo_sales/objects/<model("bmo_sales.bmo_sales"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_sales.object', {
#             'object': obj
#         })
