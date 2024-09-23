# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class MultiStockScrap(models.TransientModel):
	_name = 'multi.stock.scrap'
	_inherit = 'stock.scrap'
	_description = 'Stock Scrap Multi Location'


	