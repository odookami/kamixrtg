# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class StockQuant(models.Model):
	_inherit = 'stock.quant'

	# def _gather(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False):
	# 	res = super(StockQuant, self)._gather(product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False)
	# 	# print(res)
	# 	res = res.filtered(lambda r: not r.location_id.quarantine)
	# 	return  res