# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json

class KmiDailyUnscramble(models.Model):
	_name = 'kmi.unscramble'
	_inherit = 'kmi.daily.report'
	_order = 'revision desc'

	active = fields.Boolean('Active', default='True')
	total_reject_unscramble_a = fields.Float('Total Reject Unscramble A')
	total_reject_unscramble_b = fields.Float('Total Reject Unscramble B')
	total_reject_rinser = fields.Float('Total Reject Rinser')
	speed_max_unscramble_a = fields.Float('Speed Max Unscramble A')
	speed_max_unscramble_b = fields.Float('Speed Max Unscramble B')
	start_production_time = fields.Float('Start Production Time')
	counter_rinser = fields.Char('Counter Rinser')
	prod_note = fields.Text('Production Notes')
	parameter_mesin_notes = fields.Text(string='Parameter Mesin Notes',)
	# general_check_notes

	shift_id = fields.Many2one('res.users', string='Shift Leader', copy=False)
	unscramble_note = fields.Text(string='Another Awesome Notes', copy=False,
		default=""" 
			* Condition OK means : clean, no straching sound, in a good shape
			* SPV melakukan tanda tangan bila mereview form
			© = CCP """)

	# * o2m relations
	batch_line = fields.One2many('kmi.unscramble.batch.report', 
		'unscramble_id', string='Batch Line')
	checks_line = fields.One2many('kmi.unscramble.general.check', 
		'unscramble_id', string='General Checks')

	params_mch_line = fields.One2many('kmi.unscramble.params.value', 
		'unscramble_id', string='Parameter Machine')
	bottle_record_silo_ids = fields.One2many(
		'kmi.unscramble.bottle.line', 'unscramble_id', string='Bottle Record Silo', tracking=True
	)
	product_id = fields.Many2one('product.product',string='Product',)
	product_silo_id = fields.Many2one('product.product',string='Bottle Silo',)
	location_id = fields.Many2one('stock.location', string='Location')

	def _get_null_values(self):
		# loop batch_line
		values = [batch.batch_number for batch in self.batch_line.filtered(lambda l: not l.start_coding and l.end_coding and l.output_batch and l.reject_batch)] \
			+ [x.name for x in self.checks_line.filtered(lambda l: not l.matching)]\
			
		return values

	def check_null_value(self):
		null_values = self._get_null_values()
		if null_values:
			raise ValidationError(_('{} Belum Terisi Atau Belum Sesuai STD'.format(null_values[0])))

	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		return super(KmiDailyUnscramble, self).action_submit()

	def action_done(self):
		# self.check_null_value()
		return super(KmiDailyUnscramble, self).action_done()

	def get_model(self):
		model = self.env['kmi.unscramble'].search([('state', '=', 'model')],limit=1)
		return model

	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))
		self.write({
			'name' : model.name,
			'release_date' : model.release_date,
			'revision' : model.revision,
			'location_id' : model.location_id.id,
			'checks_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation}) for x in model.checks_line],
			'params_mch_line' : [(0,0,{'name' : x.name}) for x in model.params_mch_line],
			})

class kmiBatchReport(models.Model):
	_name = 'kmi.unscramble.batch.report'
	_inherit = 'kmi.batch.report'
	_description = 'Batch Report'

	unscramble_id = fields.Many2one('kmi.unscramble', string='Batch Report Line', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.unscramble_id), default=True)
		
class KmiUnscrambleLine(models.Model):
	_name = 'kmi.unscramble.bottle.line'
	_description = 'Kmi Unscramble Line'

	# BOTTLE RECORD SILO A & B
	silo_type = fields.Selection([
		('silo_a', 'Silo A'), ('silo_b', 'Silo B'), 
	   ], string='Tipe Silo')
	bottle_id = fields.Many2one('product.product', string='Bottle code/name')
	lot_id = fields.Many2one('stock.production.lot',string='Lot',)
	supplier = fields.Many2one('res.partner', string='Supplier')
	time = fields.Float('Time')
	bottle_in  = fields.Float('In')
	bottle_out  = fields.Float('Out')
	stock_akhir = fields.Float('Stock Akhir', compute='_compute_stock')
	unscramble_id = fields.Many2one('kmi.unscramble', string='Bottle Record Silo')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.unscramble_id), default=True)
	lot_domain = fields.Char(string='Lot Domain', compute='_compute_lot_domain')

	@api.depends('bottle_in', 'bottle_out')
	def _compute_stock(self):
		for i in self:
			i.stock_akhir = i.bottle_in - i.bottle_out

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state in ('draft','in_progress'):
				line.editable = True
			else:
				line.editable = False

	@api.depends('unscramble_id.product_id', 'unscramble_id.location_id')
	def _compute_lot_domain(self):
		for rec in self:
			rec.lot_domain = json.dumps(
					[('id', '=', False)]
				)
			# rec.lot_id = False
			quant = self.env['stock.quant']
			# lot_ids = []
			if rec.unscramble_id.product_silo_id and rec.unscramble_id.location_id:
			# koment untuk sementara
				lot_ids = quant.search([('product_id', '=', rec.unscramble_id.product_silo_id.id), 
					('location_id','=', rec.unscramble_id.location_id.id)]).mapped('lot_id').ids
				rec.lot_domain = json.dumps(
					[('id', 'in', lot_ids)]
				)
			# # yg dibawah ini biar kebuka semua
			# 	lot_ids = self.env['stock.production.lot'].search([('product_id', '=', rec.unscramble_id.product_silo_id.id)]).ids
			# 	rec.lot_domain = json.dumps(
			# 		[('id', 'in', lot_ids)]
			# 	)

class KmiGeneralCheck(models.Model):
	_name = 'kmi.unscramble.general.check'
	_inherit = 'kmi.general.checks'
	_description = 'General Checks'

	unscramble_id = fields.Many2one('kmi.unscramble', string='Unscramble')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.unscramble_id), default=True)

class KmiParamsValue(models.Model):
	_name = 'kmi.unscramble.params.value'
	_inherit = 'kmi.params.value'
	_description = 'Parameter Value'

	unscramble_id = fields.Many2one('kmi.unscramble', string='Daily Report - Machine', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.unscramble_id), default=True)