# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import date

class StockMoveLineQC(models.Model):
	_name = 'stock.move.line.qc'
	_description = 'Header untuk form QC'

	sml_ids = fields.Many2many('stock.move.line',string='Stock Move Line',)
	stock_move_id = fields.Many2one('stock.move')
	picking_id = fields.Many2one('stock.picking',string='Picking',)
	product_id = fields.Many2one('product.product',string='Product',)
	location_dest_id = fields.Many2one('stock.location',string='Destination',)
	qty = fields.Float('Qty Release')
	qty_reject = fields.Float(string='Qty Reject',)
	# lot_name = fields.Char(string='Lot Number',)
	lot_id = fields.Many2one('stock.production.lot',string='Lot Number',)
	uom_id = fields.Many2one('uom.uom',string='UoM',)
	# product_group_id = fields.Many2one('product.group',string='Premix',)
	quality_check_line = fields.One2many('inventory.quality.check','move_line_qc_id',string='Move Line QC',)
	status_qc = fields.Selection([('open', 'Open'),('reject','Reject'),('release', 'Release'),('hold', 'Hold')], default='open', string='QC Status', copy=False)
	# reason_id = fields.Many2one('inventory.reject.reason',string='Reject Reason', copy=False)
	reject_reason = fields.Text(string='Reason',)
	checked_date = fields.Date(string='QC Date', copy=False)
	check = fields.Boolean(string='Checked',)
	manufacturer_plant = fields.Many2one('manufacturer.plant',string='Manufacturer Plant',)
	origin = fields.Many2one('res.country',string='Origin', related='manufacturer_plant.country_id', store=True)
	production_date = fields.Date('Production Date')


	def check_reason_reject(self):
		if not self.reject_reason:
			raise ValidationError(_('Reject Reason harus diisi'))

	# method -> action_reject() : berikan nilai qty = qty - qty_reject dan update sml_id.qty_done = qty
	def action_reject(self):
		for rec in self:
			if any(qc_line.parameter == False  for qc_line in rec.quality_check_line):
				raise ValidationError(_('Parameter belum terisi semua.'))
			self.check_reason_reject()
			qty_release = rec.qty - rec.qty_reject
			status = 'reject' if qty_release == 0 else 'release'
			rec.write({'status_qc' : status, 'qty':qty_release, 'checked_date' : date.today(), 'reject_reason' : rec.reject_reason, 'check' : True})
			rec.lot_id.write({'karantina' : False})
			rec.qty = qty_release

	def action_hold(self):
		for rec in self:
			rec.write({'status_qc' : 'hold', 'checked_date' : date.today()})

	def action_release(self):
		for rec in self:
			if any(qc_line.parameter == False  for qc_line in rec.quality_check_line):
				raise ValidationError(_('Parameter belum terisi semua.'))
			rec.write({'status_qc' : 'release', 'checked_date' : date.today(), 'check' : True})
			qty_release = rec.qty - rec.qty_reject
			rec.qty = qty_release
			rec.lot_id.write({'karantina' : False})
			# sml_id = rec.mapped('sml_id')
			# sml_id.write({'lot_id.karantina' : False}) 

			# rec.check = True