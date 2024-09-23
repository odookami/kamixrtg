# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class bmo_closing_period(models.Model):
#     _name = 'bmo_closing_period.bmo_closing_period'
#     _description = 'bmo_closing_period.bmo_closing_period'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
