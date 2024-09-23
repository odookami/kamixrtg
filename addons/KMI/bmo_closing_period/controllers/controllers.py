# -*- coding: utf-8 -*-
# from odoo import http


# class BmoClosingPeriod(http.Controller):
#     @http.route('/bmo_closing_period/bmo_closing_period/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_closing_period/bmo_closing_period/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_closing_period.listing', {
#             'root': '/bmo_closing_period/bmo_closing_period',
#             'objects': http.request.env['bmo_closing_period.bmo_closing_period'].search([]),
#         })

#     @http.route('/bmo_closing_period/bmo_closing_period/objects/<model("bmo_closing_period.bmo_closing_period"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_closing_period.object', {
#             'object': obj
#         })
