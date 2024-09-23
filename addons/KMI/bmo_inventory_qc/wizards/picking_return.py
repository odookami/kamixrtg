# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import ValidationError



class ReturnPickingLine(models.TransientModel):
	_inherit = "stock.return.picking.line"
	_rec_name = 'product_id'
	_description = 'Return Picking Line'

	# product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('id', '=', product_id)]")
	# quantity = fields.Float("Quantity", digits='Product Unit of Measure', required=True)
	# uom_id = fields.Many2one('uom.uom', string='Unit of Measure', related='product_id.uom_id')
	# wizard_id = fields.Many2one('stock.return.picking', string="Wizard")
	# move_id = fields.Many2one('stock.move', "Move")


class ReturnPicking(models.TransientModel):
	_inherit = 'stock.return.picking'
	_description = 'Return Picking'

	@api.onchange('picking_id')
	def _onchange_picking_id(self):
		move_dest_exists = False
		product_return_moves = [(5,)]
		if self.picking_id and self.picking_id.state != 'done':
			raise UserError(_("You may only return Done pickings."))
		# In case we want to set specific default values (e.g. 'to_refund'), we must fetch the
		# default values for creation.
		line_fields = [f for f in self.env['stock.return.picking.line']._fields.keys()]
		product_return_moves_data_tmpl = self.env['stock.return.picking.line'].default_get(line_fields)
		for move in self.picking_id.move_lines:
			print(move.sml_qc_line)
			if move.state == 'cancel':
				continue
			if move.scrapped:
				continue
			if move.move_dest_ids:
				move_dest_exists = True

			if self.picking_id.picking_type_code == 'incoming':
				qc_reject = move.mapped('sml_qc_line').filtered(lambda l:l.qty_reject > 0)
				# print(qc_reject)
				if qc_reject:
					product_return_moves_data = dict(product_return_moves_data_tmpl)
					product_return_moves_data.update(self._prepare_stock_return_picking_line_vals_from_move(move))
					# print('------- product_return_moves_data -------')
					# print(product_return_moves_data)
					if product_return_moves_data['quantity'] > 0:
						product_return_moves.append((0, 0, product_return_moves_data))
						# raise ValidationError(_('No Products To Return'))	
				# print(qc_reject)
			else:
				product_return_moves_data = dict(product_return_moves_data_tmpl)
				product_return_moves_data.update(self._prepare_stock_return_picking_line_vals_from_move(move))
				print('------- product_return_moves_data -------')
				print(product_return_moves_data)
				product_return_moves.append((0, 0, product_return_moves_data))
		if self.picking_id and not product_return_moves:
			raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)."))
		if self.picking_id:
			self.product_return_moves = product_return_moves
			self.move_dest_exists = move_dest_exists
			self.parent_location_id = self.picking_id.picking_type_id.warehouse_id and self.picking_id.picking_type_id.warehouse_id.view_location_id.id or self.picking_id.location_id.location_id.id
			self.original_location_id = self.picking_id.location_id.id
			location_id = self.picking_id.location_id.id
			if self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
				location_id = self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.id
			self.location_id = location_id


	@api.model
	def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
		qc_reject = stock_move.mapped('sml_qc_line').filtered(lambda l:l.qty_reject > 0)
		# print(qc_reject.qty_reject)
		quantity = stock_move.product_qty
		if qc_reject:
			quantity = sum(x.qty_reject for x in qc_reject)
			print(quantity)
		for move in stock_move.move_dest_ids:
			if move.state in ('partially_available', 'assigned'):
				quantity -= sum(move.move_line_ids.mapped('product_qty'))
			elif move.state in ('done'):
				quantity -= move.product_qty
		quantity = float_round(quantity, precision_rounding=stock_move.product_uom.rounding)
		return {
			'product_id': stock_move.product_id.id,
			'quantity': quantity,
			'move_id': stock_move.id,
			'uom_id': stock_move.product_id.uom_id.id,
		}