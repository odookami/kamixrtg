# -*- coding: utf-8 -*-
# from odoo import http


# class BmoBatchRecord(http.Controller):
#     @http.route('/bmo_batch_record/bmo_batch_record/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_batch_record/bmo_batch_record/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_batch_record.listing', {
#             'root': '/bmo_batch_record/bmo_batch_record',
#             'objects': http.request.env['bmo_batch_record.bmo_batch_record'].search([]),
#         })

#     @http.route('/bmo_batch_record/bmo_batch_record/objects/<model("bmo_batch_record.bmo_batch_record"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_batch_record.object', {
#             'object': obj
#         })
