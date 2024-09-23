# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
from odoo.exceptions import ValidationError

class KmiLabeling(models.Model):
	_name = 'kmi.labeling'
	_inherit = 'kmi.daily.report'
	
	active = fields.Boolean('Active', default='True')
	model_id = fields.Many2one('kmi.labeling',string='Model',)

	product_labeling_id = fields.Many2one('product.product',string='Product Labeling',)
	location_id = fields.Many2one('stock.location', string='Location')

	# * o2m relations
	batch_line = fields.One2many('kmi.labeling.batch.report', 
		'labeling_id', string='Batch Line')
	verify_coding_line = fields.One2many('kmi.labeling.verify.coding', 'labeling_id', string='Verifikasi Coding')
	checks_line = fields.One2many('kmi.labeling.general.checks', 'labeling_id', string='General Checks')
	checks_line_1 = fields.One2many('kmi.labeling.general.checks', 'labeling_id', string='General Checks 1', domain=[('group','=','1'), ])
	checks_line_2 = fields.One2many('kmi.labeling.general.checks', 
		'labeling_id', string='General Checks 2', domain=[('group','=','2'), ])
	params_mch_line = fields.One2many('kmi.labeling.params.value', 'labeling_param_seal_id', string='Production Machine ',)
	prod_rec_line = fields.One2many('kmi.labeling.params.value', 'labeling_id', string='Production Record')
	prod_rec_1_line = fields.One2many('kmi.labeling.params.value', 'labeling_id', string='Production Record 1', domain=[('group','=','1'), ])
	prod_rec_2_line = fields.One2many('kmi.labeling.params.value', 'labeling_id', string='Production Record 2', domain=[('group','=','2'), ])
	prod_rec_3_line = fields.One2many('kmi.labeling.params.value', 'labeling_id', string='Production Record 1', domain=[('group','=','3'), ])

	conversion_line = fields.One2many('kmi.labeling.params.value', 
		'labeling_id', string='Roll to Kg Reject Qty Conversion', domain=[('group','=','4'), ])
	material_line = fields.One2many('kmi.labeling.material.usage', 
		'labeling_id', string='Material Usage')
	incompatibility_line = fields.One2many('kmi.labeling.incompatibility.notes', 
		'labeling_id', string='Catatan Proses Produksi')
	
	note_checks = fields.Text('Note General Checks')
	note_vefiri_coding = fields.Text('Verifikasi Coding Box')
	note_prod_rec = fields.Text('Note Production Record')
	batch_1 = fields.Char(string='Batch 1',)
	batch_2 = fields.Char(string='Batch 2',)
	batch_3 = fields.Char(string='Batch 3',)
	batch_note_1 = fields.Char(string='Batch Notes 1',)
	batch_note_2 = fields.Char(string='Batch Notes 2',)
	batch_note_3 = fields.Char(string='Batch Notes 3',)
	material_usage_note = fields.Text(string='Notes',)
	labeling_note = fields.Text(string='Another Awesome Notes', copy=False,
		default="""	 * Condition OK means : clean, no straching sound, in a good shape
		* Machine stop under 30 min ditulis pada minor breakdown (Form Efficiency)
		* SPV melakukan tanda tangan bila mereview form
		* Bila belt leak check kotor, segera dibersihkan dengan brush dan air per 2 jam
		* Reject SLA yang dibuang pada saat produksi """)

	# * GENERAL REPORT
	downtime = fields.Float(string='Downtime')
	total_reject_btl = fields.Float(string='Total Reject Botol')
	total_reject_lbl = fields.Float(string='Total Reject Label')
	product_name = fields.Char(string='Product name')
	output_batch = fields.Float(string='Output / Batch')
	reject_batch = fields.Float(string='Reject / Batch')
	parameter_mesin_notes = fields.Text(string='Parameter Mesin Notes',)

	def insert_production_record(self, batch_line):
		# print(values)
		if self.prod_rec_1_line:
			existing_group = self.prod_rec_1_line.mapped('group')
			next_group = int(existing_group[len(existing_group) - 1]) + 1
			if next_group > 8:
				raise ValidationError(_('Anda tidak dapat menambahkan lebih dari 8 batch ke transaksi ini'))
			self.write({
				'{}'.format('batch_'+ str(next_group)) : batch_line,
				'prod_rec_1_line' : [(0,0,{'name' : line.name, 'group' : str(next_group)}) for line in self.model_id.prod_rec_1_line]
				})
			# print(next_group)
		else:
			self.write({
				'batch_1' : batch_line,
				'prod_rec_1_line' : [(0,0,{'name' : line.name, 'group' : '1'}) for line in self.model_id.prod_rec_1_line]
				})

	def _get_null_values(self):
		# loop batch_line
		values = [batch.batch_number for batch in self.batch_line.filtered(lambda l: not l.start_coding and l.end_coding and l.output_batch and l.reject_batch)] \
			+ [check.name for check in self.checks_line.filtered(lambda l: not l.matching)]\
			
		return values

	def check_null_value(self):
		null_values = self._get_null_values()
		if null_values:
			raise ValidationError(_('{} Belum Terisi Atau Belum Sesuai STD'.format(null_values[0])))

	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		return super(KmiLabeling, self).action_submit()

	def action_done(self):
		# self.check_null_value()
		return super(KmiLabeling, self).action_done()

	def get_model(self):
		model = self.env['kmi.labeling'].search([('state', '=', 'model')],limit=1)
		return model

	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))
		self.write({
			'name' : model.name,
			'revision' : model.revision,
			'release_date' : model.release_date,
			'location_id' : model.location_id.id,
			'model_id' : model.id,
			'checks_line_1' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'group' : '1'}) for x in model.checks_line_1],
			'checks_line_2' : [(0,0,{'item' : x.item, 'group' : '2'}) for x in model.checks_line_2],
			'params_mch_line' : [(0,0,{'name' : x.name, }) for x in model.params_mch_line],
			'prod_rec_1_line' : [(0,0,{'name' : x.name, 'group' : '1'}) for x in model.prod_rec_line],
			'prod_rec_2_line' : [(0,0,{'name' : x.name, 'group' : '2'}) for x in model.prod_rec_line],
			'prod_rec_3_line' : [(0,0,{'name' : x.name, 'group' : '3'}) for x in model.prod_rec_line],
			})

class kmiBatchReport(models.Model):
	_name = 'kmi.labeling.batch.report'
	_inherit = 'kmi.batch.report'

	labeling_id = fields.Many2one('kmi.labeling', 
		string='Batch Report Line', ondelete='cascade')
	prod_rec_line = fields.One2many('kmi.labeling.params.value','batch_report_id',string='Labeling Params',)
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.labeling_id), default=True)

	# prod_rec_created = fields.Boolean(string='Production Record Created',)
	# def insert_production_record(self):
	# 	# print(values)
	# 	self.ensure_one()
	# 	if self.labeling_id.prod_rec_line:
	# 		existing_group = self.labeling_id.prod_rec_line.mapped('group')
	# 		next_group = int(existing_group[len(existing_group) - 1]) + 1
	# 		if next_group > 8:
	# 			raise ValidationError(_('Anda tidak dapat menambahkan lebih dari 8 batch ke transaksi ini'))
	# 		self.labeling_id.write({
	# 			'{}'.format('batch_'+ str(next_group)) : self.batch_number,
	# 			'prod_rec_line' : [(0,0,{'name' : line.name, 'group' : str(next_group)}) for line in self.labeling_id.model_id.prod_rec_line]
	# 			})
	# 		# print(next_group)
	# 	else:
	# 		self.labeling_id.write({
	# 			'batch_1' : self.batch_number,
	# 			'prod_rec_line' : [(0,0,{'name' : line.name, 'group' : '1'}) for line in self.labeling_id.model_id.prod_rec_line]
	# 			})
	# 	self.write({'prod_rec_created':True})

class KmiLabelingVerifyCoding(models.Model):
	_name = 'kmi.labeling.verify.coding'
	_inherit = 'kmi.verify.coding'

	labeling_id = fields.Many2one('kmi.labeling', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.labeling_id), default=True)

class KmiGeneralCheck(models.Model):
	_name = 'kmi.labeling.general.checks'
	_inherit = 'kmi.general.checks'

	item = fields.Char(string='Item')
	vjb  = fields.Char(string='VJ-B')

	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),
		('4', '4'),
		('5', '5'),
		('6', '6'),
		('7', '7'),
		('8', '8'),], string='Line Position')

	labeling_id = fields.Many2one('kmi.labeling', string='Labeling')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.labeling_id), default=True)

class KmiParamsValue(models.Model):
	_name = 'kmi.labeling.params.value'
	_inherit = 'kmi.params.value'
	_description = 'Parameter Value'

	labeling_id = fields.Many2one('kmi.labeling', string='Daily Report - Machine', ondelete='cascade')
	labeling_param_seal_id = fields.Many2one('kmi.labeling', string='Production Machine', ondelete='cascade')
	batch_report_id = fields.Many2one('kmi.labeling.batch.report',string='Batch Report',)

	param_17 = fields.Char('17')
	param_18 = fields.Char('18')
	param_19 = fields.Char('19')
	param_20 = fields.Char('20')
	param_21 = fields.Char('21')
	param_22 = fields.Char('22')
	param_23 = fields.Char('23')
	param_24 = fields.Char('24')

	product_type = fields.Selection(string='Product', 
		selection=[('Produk CGM/HI C', 'Produk CGM/HI C'), 
		('Produk NBE/Fishot', 'Produk NBE/Fishot'),])

	reject_pcs = fields.Float(string='Reject pcs', 
		 readonly=False)
	reject_cm = fields.Float(string='Reject cm')

	reject_pcs_m = fields.Float(string='m (Reject pcs)', 
		 compute='_compute_rpcs_m', readonly=False)
	reject_cm_m = fields.Float(string='m (Reject cm)', 
		 compute='_compute_cm_m', readonly=False)

	std_pcs = fields.Float(string='Std pcs (m)', default='1000')
	std_cm = fields.Float(string='Std cm (m)', default='1000')

	reject_rpcs = fields.Float(string='Reject pcs', 
		 compute='_compute_rrpcs', readonly=False)
	reject_rcm = fields.Float(string='Reject cm', 
		 compute='_compute_rrcm', readonly=False)
	total_reject = fields.Float(string='Total Reject', 
		 compute='_compute_total', readonly=False)

	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),
		('4', '4'),
		('5', '5'),
		('6', '6'),
		('7', '7'),
		('8', '8'),], string='Line Position')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.labeling_id), default=True)

	@api.depends('reject_pcs')
	def _compute_rpcs_m(self):
		for record in self:
			result = (record.reject_pcs * 10.3) / 100 if record.reject_pcs else 0
			record.reject_pcs_m = result if record.reject_pcs_m <= 0 else 0
	
	@api.depends('reject_cm')
	def _compute_cm_m(self):
		for record in self:
			result = (record.reject_cm / 100) if record.reject_cm else 0
			record.reject_cm_m = result if record.reject_cm_m <= 0 else 0
	
	@api.depends('reject_pcs_m', 'std_pcs')
	def _compute_rrpcs(self):
		for record in self:
			result = (record.reject_pcs_m / record.std_pcs) \
				if record.reject_pcs_m and record.std_pcs else 0
			record.reject_rpcs = result if record.reject_rpcs <= 0 else 0
	
	@api.depends('reject_cm_m', 'std_cm')
	def _compute_rrcm(self):
		for record in self:
			result = (record.reject_cm_m / record.std_cm) \
				if record.reject_cm_m and record.std_cm else 0
			record.reject_rcm = result if record.reject_rcm <= 0 else 0
	
	@api.depends('reject_rpcs', 'reject_rcm')
	def _compute_total(self):
		for record in self:
			result = record.reject_rpcs + record.reject_rcm
			record.total_reject = result if record.total_reject <= 0 else 0

class Kmilabeling2MaterialUsage(models.Model):
	_name = 'kmi.labeling.material.usage'
	_inherit = 'kmi.material.usage'

	first_stock = fields.Float('First stock (Netto)')
	in_qty = fields.Float('In minutes', compute='_compute_in_minute')
	reject = fields.Float('Reject')
	note = fields.Text('Notes')
	lot_id = fields.Many2one('stock.production.lot',string='Lot',)
	lot_domain = fields.Char(string='Lot Domain', compute='_compute_lot_domain')
	fs_manual = fields.Float("Qty Manual")

	labeling_id = fields.Many2one('kmi.labeling', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.labeling_id), default=True)

	@api.depends('start', 'finish')
	def _compute_in_minute(self):
		for record in self:
			result = record.finish - record.start
			record.in_qty = result if record.in_qty <= 0 else 0

	@api.depends('labeling_id.product_labeling_id', 'labeling_id.location_id')
	def _compute_lot_domain(self):
		for rec in self:
			rec.lot_domain = json.dumps([('id', '=', 0)])
			# rec.lot_id = False
			quant = self.env['stock.quant']
			# lot_ids = []
			if rec.labeling_id.product_labeling_id and rec.labeling_id.location_id:
			# koment untuk sementara
				lot_ids = quant.search([('product_id', '=', rec.labeling_id.product_labeling_id.id), 
					('location_id','=', rec.labeling_id.location_id.id)]).mapped('lot_id').ids
				rec.lot_domain = json.dumps(
					[('id', 'in', lot_ids)]
				)
			# yg dibawah ini biar kebuka semua
				# lot_ids = self.env['stock.production.lot'].search([('product_id', '=', rec.labeling_id.product_labeling_id.id)]).ids
				# rec.lot_domain = json.dumps(
				# 	[('id', 'in', lot_ids)]
				#)

class KmiIncompatibilityNotes(models.Model):
	_name = 'kmi.labeling.incompatibility.notes'
	_inherit = 'kmi.incompatibility.notes'

	labeling_id = fields.Many2one('kmi.labeling', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.labeling_id), default=True)

	total = fields.Float(string='Total', compute='_compute_total_hour')

	@api.depends('start', 'finish')
	def _compute_total_hour(self):
		for record in self:
			result = record.finish - record.start
			record.total = result if record.total <= 0 else 0