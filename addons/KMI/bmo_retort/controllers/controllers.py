# -*- coding: utf-8 -*-
# from odoo import http


# class BmoProductSt(http.Controller):
#     @http.route('/bmo_product_st/bmo_product_st/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bmo_product_st/bmo_product_st/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bmo_product_st.listing', {
#             'root': '/bmo_product_st/bmo_product_st',
#             'objects': http.request.env['bmo_product_st.bmo_product_st'].search([]),
#         })

#     @http.route('/bmo_product_st/bmo_product_st/objects/<model("bmo_product_st.bmo_product_st"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bmo_product_st.object', {
#             'object': obj
#         })
