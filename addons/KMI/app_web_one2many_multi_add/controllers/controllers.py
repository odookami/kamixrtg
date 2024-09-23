# -*- coding: utf-8 -*-
from odoo import http

# class RtOne2manyMultiSelection(http.Controller):
#     @http.route('/app_web_one2many_multi_add/app_web_one2many_multi_add/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/app_web_one2many_multi_add/app_web_one2many_multi_add/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('app_web_one2many_multi_add.listing', {
#             'root': '/app_web_one2many_multi_add/app_web_one2many_multi_add',
#             'objects': http.request.env['app_web_one2many_multi_add.app_web_one2many_multi_add'].search([]),
#         })

#     @http.route('/app_web_one2many_multi_add/app_web_one2many_multi_add/objects/<model("app_web_one2many_multi_add.app_web_one2many_multi_add"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('app_web_one2many_multi_add.object', {
#             'object': obj
#         })