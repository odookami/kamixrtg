# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class UpdateLotNumber(models.TransientModel):
	_name = 'update.lot.number'
	_description = 'Update Lot Number'

	picking_id = fields.Many2one('stock.picking',string='Transfers',)
	update_lot_number_line = fields.One2many('update.lot.number.line','update_id',string='Lot Number Line',)

	# @api.model
	# def default_get(self, fields):
	# 	res = super(UpdateLotNumber, self).default_get(fields)
		
	# 	return res

	@api.onchange('picking_id')
	def onchange_picking_id(self):
		self.update_lot_number_line = False
		if self.picking_id:
			lot_ids = self.env['stock.production.lot'].search([('picking_id', '=', self.picking_id.id)])
			self.update_lot_number_line = [(0,0,{
				'lot_id' : lot.id,
				# ''
				}) for lot in lot_ids]

	def button_update_lot_number(self):
		for line in self.update_lot_number_line:
			line.lot_id.write({'name' : line.update_lot_number})


class UpdateLotNumberLine(models.TransientModel):
	_name = 'update.lot.number.line'
	_description = 'Update Lot Number Line'


	update_id = fields.Many2one('update.lot.number',string='Update Lot Number',)
	lot_id = fields.Many2one('stock.production.lot',string='Lot Number',)
	picking_id = fields.Many2one('stock.picking', related='lot_id.picking_id')
	update_lot_number = fields.Char('Update Number')


