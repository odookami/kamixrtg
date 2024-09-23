# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MrpProductionType(models.Model):
    _name = 'mrp.production.type'
    _description = 'Production Type'

    name = fields.Char(string='Name')
    code = fields.Char(string='code', copy=False)

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 
        'Code must be unique, this one already assigned !'),
    ]