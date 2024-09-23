# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class QcTransferRejectWizard(models.TransientModel):
	_name = 'qc.transfer.reject.wizard'
	_inherit = 'stock.scrap'
	_description = 'QC Transfer Reject Wizard'

	quality_check_finish_good_id = fields.Many2one('quality.check.finish.good',string='QC Finish Goods',)
	transfer_reject_line = fields.One2many('transfer.reject.line','transfer_reject_id',string='Transfer Reject',)

	@api.model
	def default_get(self, fields):
		res = super(QcTransferRejectWizard, self).default_get(fields)
		active_ids = self._context.get('active_ids')
		qc_fg_id = self.env['quality.check.finish.good'].browse(active_ids)

		transfer_reject_line = qc_fg_id.qcfg_line.filtered(lambda l:l.state == 'reject')
		# print(transfer_reject_line)
		res.update({
			'master_type_id' : self.env.ref('bmo_qc_fg.qc_fg_scrap_type_id').id,
			'quality_check_finish_good_id' : qc_fg_id.id,
			'product_id'	: qc_fg_id.product_id.id,
			'product_uom_id' : qc_fg_id.product_id.uom_id.id,
			'transfer_reject_line' : [(0,0,{
				'location_id' : line.location_id.id,
				'product_id' : qc_fg_id.product_id.id,
				'lot_id' : line.lot_id.id,
				'qty' : line.qty,
				}) for line in transfer_reject_line]
			})
		return res

	def action_create_transfer(self):
		values = [{
			'master_type_id' : self.env.ref('bmo_qc_fg.qc_fg_scrap_type_id').id,
			'location_id' : line.location_id.id,
			'scrap_location_id': self.scrap_location_id.id,
			'lot_id' : line.lot_id.id,
			'scrap_qty' : line.qty,
			'product_uom_id' : line.product_id.uom_id.id,
			'product_id' : line.product_id.id
		} for line in self.transfer_reject_line]

		scrap_ids = self.env['stock.scrap'].create(values)
		# scrap_ids.action_validate()
		for scrap in scrap_ids:
			scrap.action_validate()
			print('VALIDATED')
		source_location_ids = self.transfer_reject_line.mapped('location_id')
		source_location_ids.write({'quarantine' : False})
		self.quality_check_finish_good_id.write({'scrap' : True})
		return {
			'name': _('QC Finish Good Reject'),
			'view_mode': 'tree,form',
			'res_model': 'stock.scrap',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', scrap_ids.ids)],
			# 'context': {
			# 	'journal_id': self.journal_id.id,
			# }
		}
		# print('CREATE TRANSFER')


class QcTransferRejectLineWizard(models.TransientModel):
	_name = 'transfer.reject.line'
	_description = 'QC Transfer Reject Line'


	transfer_reject_id = fields.Many2one('qc.transfer.reject.wizard',string='Transfer Reject ID',)
	location_id = fields.Many2one('stock.location',string='Location',)
	product_id = fields.Many2one('product.product',string='Product',)
	lot_id = fields.Many2one('stock.production.lot',string='Lot Number',)
	qty = fields.Float(string='Quantity Reject',)
	