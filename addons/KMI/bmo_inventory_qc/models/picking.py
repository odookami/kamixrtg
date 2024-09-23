# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import re
import simplejson as json

class Picking(models.Model):
	_inherit = 'stock.picking'

	state = fields.Selection(selection_add=[('approval_1', 'Warehouse'),('approval_2', 'QC'),('approval_3', 'Approval 3'),('done',)])
	picking_quality_check_line = fields.One2many('inventory.quality.check','picking_id',string='QC Line',copy=False)
	warehouse_reject = fields.Boolean(string='Warehouse Reject',)
	stock_move_quality_check_line = fields.One2many('stock.move.line.qc','picking_id',string='SML QC Line',)
	show_qc_checked = fields.Boolean(string='Show QC Check', compute='_compute_status_qc')
	show_qc_open = fields.Boolean(string='Show QC Open', compute='_compute_status_qc')
	show_qc_hold = fields.Boolean(string='Show QC Open', compute='_compute_status_qc')
	show_qc_form = fields.Boolean(string='Show QC Form', compute='_show_qc_form')
	value_qc = fields.Char(compute='_compute_value_qc', string='Status Qc')
	
	@api.depends('show_qc_checked','state')
	def _compute_value_qc(self):
		for o in self:
			if o.show_qc_checked:
				o.value_qc = 'Checked'
			else:
				o.value_qc = ''
	

	@api.depends('state', 'picking_type_code')
	def _show_qc_form(self):
		for rec in self:
			rec.show_qc_form = True if rec.state == 'done' and rec.picking_type_code == 'incoming' and rec.delivery_return == False else False
			# if rec.state == 'done' and rec.picking_type_code == 'incoming':
			# 	rec.show_qc_form = True

	@api.depends('stock_move_quality_check_line', 'show_qc_form')
	def _compute_status_qc(self):
		for rec in self:
			# if rec.picking_type_code == 'incoming':
			if not any(qcl.status_qc in ['open', 'hold'] for qcl in rec.stock_move_quality_check_line) and rec.state == 'done' \
			and rec.picking_type_code == 'incoming' and rec.stock_move_quality_check_line and rec.show_qc_form == True:
				rec.show_qc_checked, rec.show_qc_open, rec.show_qc_hold = [True, False, False]
			elif any(qcl.status_qc == 'open' for qcl in rec.stock_move_quality_check_line) and rec.state == 'done' \
			and rec.picking_type_code == 'incoming' and rec.stock_move_quality_check_line and rec.show_qc_form == True:
				rec.show_qc_checked, rec.show_qc_open, rec.show_qc_hold  = [False, True, False]
			elif any(qcl.status_qc == 'hold' for qcl in rec.stock_move_quality_check_line) and rec.state == 'done' \
			and rec.picking_type_code == 'incoming' and rec.stock_move_quality_check_line and rec.show_qc_form == True:
				rec.show_qc_checked, rec.show_qc_open, rec.show_qc_hold  = [False, False, True]
			else:
				rec.show_qc_checked = rec.show_qc_open = rec.show_qc_hold = False


	def button_submit_approval(self):
		# self._create_qc()
		self.write({'state':'approval_1'}) if not self.warehouse_reject else self._create_qc()

	def button_approval_1(self):
		allowance_percent = self.env.company.receipt_allowance / 100
		for picking in self:
			if not picking.move_line_nosuggest_ids:
				raise ValidationError(_('Detail Operations harus diisi'))
			# move_with_allowance --> mencari stock_move yg memiliki kondisi quantity_done > total allowance max atau quantity_done < total allowance min
			move_with_allowance = picking.move_lines.filtered(lambda sm:sm.quantity_done > sm.product_uom_qty + (sm.product_uom_qty * allowance_percent) or\
				sm.quantity_done < sm.product_uom_qty - (sm.product_uom_qty * allowance_percent))
			picking._back_to_ppic() if move_with_allowance else picking._create_qc()

	def button_validate(self):
		allowance_percent = self.env.company.receipt_allowance / 100
		for picking in self:
			# for line in picking.move_line_nosuggest_ids:
			# 	if not line.lot_name or not line.expiration_date and picking.picking_type_code == 'incoming':
			# 			raise ValidationError(_('Lot name atau Expiration Date belum diisi'))
			# move_with_allowance --> mencari stock_move yg memiliki kondisi quantity_done > total allowance max atau quantity_done < total allowance min
			move_with_allowance = picking.move_lines.filtered(lambda sm:sm.quantity_done > sm.product_uom_qty + (sm.product_uom_qty * allowance_percent) or\
				sm.quantity_done < sm.product_uom_qty - (sm.product_uom_qty * allowance_percent))
			if move_with_allowance and picking.picking_type_code == 'incoming' and picking.warehouse_reject != True:
				print('emang masuk sini ???')
				return picking._back_to_ppic()
		res = super(Picking, self).button_validate()
		if self.picking_type_code == 'incoming':
			self._create_qc()
		return res

	def button_approval_2(self):
		self.write({'state':'approval_3'})

	def _back_to_ppic(self):
		self.write({'state' : 'assigned', 'warehouse_reject' : True})

	def get_qc_values(self):
		template_ids = self.env['inventory.quality.check.template'].sudo().search([])
		qc_values = [(0,0,{
			'name' :  template.name,
			'sequence' : template.sequence,
			'picking_id' : self.id,
		}) for template in template_ids]
		return qc_values

	def _create_qc(self):
		for rec in self:
			qc_values = rec.get_qc_values()
			qc_line_values = rec.move_line_nosuggest_ids.create_qc(qc_values)
			qc_write_vals = [(0,0,vals) for key, vals in qc_line_values.items()]
			# print(json.dumps(qc_write_vals, indent=2))
			return rec.write({'stock_move_quality_check_line' : qc_write_vals})

class StockMove(models.Model):
	_inherit = 'stock.move'

	state = fields.Selection(selection_add=[('approval_1', 'Warehouse'),('approval_2', 'QC'),('approval_3', 'Approval 3'),('done',)])
	sml_qc_line = fields.One2many('stock.move.line.qc','stock_move_id')

