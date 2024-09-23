# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class bmo_product_st(models.Model):
#     _name = 'bmo_product_st.bmo_product_st'
#     _description = 'bmo_product_st.bmo_product_st'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
