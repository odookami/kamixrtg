# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class StockLocation(models.Model):
	_inherit = 'stock.location'

	allow_quarantine = fields.Boolean(string='Allow Quarantine',)
	quarantine = fields.Boolean(string='Quarantine',)

	# def name_get(self)

class StockQuantPackage(models.Model):
	_inherit = 'stock.quant.package'
	_order = 'name asc'
	