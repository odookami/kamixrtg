# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class bmo_report_okp(models.Model):
#     _name = 'bmo_report_okp.bmo_report_okp'
#     _description = 'bmo_report_okp.bmo_report_okp'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
