# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class StockMove(models.Model):
	_inherit = 'stock.move'

	info_po = fields.Char(related='sale_line_id.info_po')