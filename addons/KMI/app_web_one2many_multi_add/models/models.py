# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class app_web_one2many_multi_add(models.Model):
#     _name = 'app_web_one2many_multi_add.app_web_one2many_multi_add'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100