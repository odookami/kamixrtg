# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    bache_id = fields.Many2one(
        comodel_name='batch.mrp.production', string='OKP', copy=False)
    mo_id = fields.Many2one(
        "mrp.production", "MO")
    okp_id = fields.Many2one("mrp.okp", "OKP")