# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
from odoo.exceptions import ValidationError

class KmiPacking(models.Model):
	_name = 'kmi.packing'
	_inherit = 'kmi.daily.report'

	active = fields.Boolean('Active', default='True')
	model_id = fields.Many2one('kmi.packing',string='Model',)
	# editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_daily_report_id), default=True)
	product_packing_id = fields.Many2one('product.product',string='Product Packing',)
	location_id = fields.Many2one('stock.location', string='Location')

	material_usage_note = fields.Text(string='Note')
	material_usage_sample = fields.Text(string='Sample')
	note_checks = fields.Text('Note General Checks')
	note_vefiri_coding = fields.Text('Verifikasi Coding Box')

	packing_note = fields.Text(string='Another Awesome Notes', copy=False,
		default=""" * Condition OK means : clean, no straching sound, in a good shape
		* Machine stop under 30 min ditulis pada minor breakdown (Form Efficiency)
		* SPV melakukan tanda tangan bila mereview form
			""")

	# * o2m relations
	batch_line = fields.One2many('kmi.packing.batch.report', 
		'packing_id', string='Batch Line')
	checks_line = fields.One2many('kmi.packing.general.checks', 
		'packing_id', string='General Checks')
	checks_1_line = fields.One2many('kmi.packing.general.checks', 
		'packing_id', string='General Checks', domain=[('group','=','1'), ])
	checks_2_line = fields.One2many('kmi.packing.general.checks', 
		'packing_id', string='General Checks', domain=[('group','=','2'), ])
	checks_3_line = fields.One2many('kmi.packing.general.checks', 
		'packing_id', string='General Checks', domain=[('group','=','3'), ])
	checks_4_line = fields.One2many('kmi.packing.general.checks', 
		'packing_id', string='General Checks', domain=[('group','=','4'), ])
	checks_5_line = fields.One2many('kmi.packing.general.checks', 
		'packing_id', string='General Checks', domain=[('group','=','5'), ])
	checks_6_line = fields.One2many('kmi.packing.general.checks', 
		'packing_id', string='General Checks', domain=[('group','=','6'), ])
	verify_coding_line = fields.One2many('kmi.packing.verify.coding', 'packing_id', string='Verifikasi Coding')
	material_line = fields.One2many('kmi.packing.material.usage', 
		'packing_id', string='Material Usage')
	incompatibility_line = fields.One2many('kmi.packing.incompatibility.notes', 
		'packing_id', string='Catatan Proses Produksi')
	
	def insert_production_record(self, batch_line):
		# print(values)
		if self.prod_rec_line:
			existing_group = self.prod_rec_line.mapped('group')
			next_group = int(existing_group[len(existing_group) - 1]) + 1
			if next_group > 8:
				raise ValidationError(_('Anda tidak dapat menambahkan lebih dari 8 batch ke transaksi ini'))
			self.write({
				'{}'.format('batch_'+ str(next_group)) : batch_line,
				'prod_rec_line' : [(0,0,{'name' : line.name, 'group' : str(next_group)}) for line in self.model_id.prod_rec_line]
				})
			# print(next_group)
		else:
			self.write({
				'batch_1' : batch_line,
				'prod_rec_line' : [(0,0,{'name' : line.name, 'group' : '1'}) for line in self.model_id.prod_rec_line]
				})

	def _get_null_values(self):
		# loop batch_line
		values = [batch.batch_number for batch in self.batch_line.filtered(lambda l: not l.start_coding and l.end_coding and l.output_batch and l.reject_batch)] \
			+ [check.name for check in self.checks_1_line.filtered(lambda l: not l.matching)]\
			+ [check.name for check in self.checks_2_line.filtered(lambda l: not l.matching)]\
			+ [check.name for check in self.checks_3_line.filtered(lambda l: not l.matching)]\
			+ [check.name for check in self.checks_4_line.filtered(lambda l: not l.matching)]

		return values

	def check_null_value(self):
		null_values = self._get_null_values()
		if null_values:
			raise ValidationError(_('{} Belum Terisi Atau Belum Sesuai STD'.format(null_values[0])))
	
	def get_model(self):
		model = self.env['kmi.packing'].search([('state', '=', 'model')],limit=1)
		return model
	
	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		return super(KmiPacking, self).action_submit()
	
	def action_done(self):
		# self.check_null_value()
		return super(KmiPacking, self).action_done()
	
	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))
		self.write({
			'name' : model.name,
			'revision' : model.revision,
			'release_date' : model.release_date,
			'location_id' : model.location_id.id,
			'model_id' : model.id,
			'checks_1_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'group' : '1'}) for x in model.checks_1_line],
			'checks_2_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'group' : '2'}) for x in model.checks_2_line],
			'checks_3_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'group' : '3'}) for x in model.checks_3_line],
			'checks_4_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'group' : '4'}) for x in model.checks_4_line],
			'checks_5_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'group' : '5'}) for x in model.checks_5_line],
			# 'prod_rec_1_line' : [(0,0,{'name' : x.name,}) for x in model.prod_rec_line],
			# 'prod_rec_2_line' : [(0,0,{'name' : x.name,}) for x in model.prod_rec_line],
			})

class kmiBatchReport(models.Model):
	_name = 'kmi.packing.batch.report'
	_inherit = 'kmi.batch.report'

	packing_id = fields.Many2one('kmi.packing', 
		string='Batch Report Line', ondelete='cascade')
	start_pallet = fields.Char('Start Pallet')
	end_pallet = fields.Char('Finish Pallet')
	prod_rec_line = fields.One2many('kmi.packing.params.value','batch_report_id',string='Packing Params',)
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.packing_id), default=True)

class KmiGeneralCheck(models.Model):
	_name = 'kmi.packing.general.checks'
	_inherit = 'kmi.general.checks'

	packing_id = fields.Many2one('kmi.packing', string='Packing', ondelete='cascade')
	reject_bo = fields.Char('BO')
	reject_qty = fields.Integer('QTY')
	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),
		('4', '4'),
		('5', '5'),
		('6', '6'),
		('7', '7'),
		('8', '8'),], string='Line Position')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.packing_id), default=True)

class KmiPackingVerifyCoding(models.Model):
	_name = 'kmi.packing.verify.coding'
	_inherit = 'kmi.verify.coding'

	packing_id = fields.Many2one('kmi.packing', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.packing_id), default=True)

class KmiPackingMaterialUsage(models.Model):
	_name = 'kmi.packing.material.usage'
	_inherit = 'kmi.material.usage'

	first_stock = fields.Float('First stock (Netto)')
	in_minute = fields.Float('In minutes')
	reject = fields.Float('Reject')
	sample_qc = fields.Float('Sample QC')
	note = fields.Text('Notes')
	lot_id = fields.Many2one('stock.production.lot',string='Lot',)
	lot_domain = fields.Char(string='Lot Domain', compute='_compute_lot_domain')
	last_stock = fields.Float(string='Last stock', compute='_compute_last_stock',)

	packing_id = fields.Many2one('kmi.packing', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.packing_id), default=True)

	@api.depends('in_qty','out_qty', 'sample_qc', 'reject_machine_qty', 'reject_coding_qty', 'reject_supplier_qty')
	def _compute_last_stock(self):
		for record in self:
			# result = 0
			# material_line = record.packing_id.material_line
			result = record.in_qty - record.out_qty - record.sample_qc - record.reject_machine_qty - record.reject_coding_qty - record.reject_supplier_qty
			record.last_stock = result if record.last_stock <= 0 else 0

	@api.depends('packing_id.product_packing_id', 'packing_id.location_id')
	def _compute_lot_domain(self):
		for rec in self:
			rec.lot_domain = json.dumps([('id', '=', 0)])
			# rec.lot_id = False
			quant = self.env['stock.quant']
			# lot_ids = []
			if rec.packing_id.product_packing_id and rec.packing_id.location_id:
			# koment untuk sementara
				lot_ids = quant.search([('product_id', '=', rec.packing_id.product_packing_id.id), 
					('location_id','=', rec.packing_id.location_id.id)]).mapped('lot_id').ids
				rec.lot_domain = json.dumps(
					[('id', 'in', lot_ids)]
				)
			# yg dibawah ini biar kebuka semua
				# lot_ids = self.env['stock.production.lot'].search([('product_id', '=', rec.packing_id.product_packing_id.id)]).ids
				# rec.lot_domain = json.dumps(
				# 	[('id', 'in', lot_ids)]
				#)

class KmiIncompatibilityNotes(models.Model):
	_name = 'kmi.packing.incompatibility.notes'
	_inherit = 'kmi.incompatibility.notes'

	packing_id = fields.Many2one('kmi.packing', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.packing_id), default=True)

	total = fields.Float(string='Total', compute='_compute_total_hour')

	@api.depends('start', 'finish')
	def _compute_total_hour(self):
		for record in self:
			result = record.finish - record.start
			record.total = result if record.total <= 0 else 0

class KmiParamsValue(models.Model):
	_name = 'kmi.packing.params.value'
	_inherit = 'kmi.params.value'

	packing_id = fields.Many2one('kmi.packing', 
		string='Daily Report - Production Record', ondelete='cascade')
	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),
		('4', '4'),
		('5', '5'),
		('6', '6'),
		('7', '7'),
		('8', '8'),], string='Line Position')	
	batch_report_id = fields.Many2one('kmi.packing.batch.report',string='Batch Report',)
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.packing_id), default=True)
