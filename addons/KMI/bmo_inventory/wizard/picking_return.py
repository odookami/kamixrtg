# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class StockReturnPicking(models.TransientModel):
	_inherit = 'stock.return.picking'

	def _create_returns(self):
		res = super(StockReturnPicking, self)._create_returns()
		new_picking_id, picking_type_id = res
		new_picking = self.env['stock.picking'].browse([new_picking_id])
		picking_type = self.env['stock.picking.type'].browse([picking_type_id])
		if self.picking_id.picking_type_code == 'outgoing':
			new_picking.write({'delivery_return' : True, 'picking_return_id': self.picking_id.id})

		return res