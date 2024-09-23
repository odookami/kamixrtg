# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import re

class KmiDailyReport(models.AbstractModel):
	_name = 'kmi.daily.report'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Laporan Harian'

	name = fields.Char(string='No. Dok', 
		default='FRM-PRD-', copy=False)
	num_of_pages = fields.Char(string='Hal')
	revision = fields.Integer(string='Revisi')
	state = fields.Selection([
		('draft', 'Draft'), 
		('in_progress', 'In Progress'),
		('done', 'Done'), 
		('draft_model', 'Draft'),
		('model', 'Model'),
		('cancel', 'Cancel')], 'Status', default='draft', tracking=True, copy=False)
	report_type = fields.Selection([('Packing', 'Packing'), ('Labeling', 'Labeling'), 
		('UnLoader', 'UnLoader'), ('Retort', 'Retort'), ('Loader', 'Loader'),
		('Unscramble Machine', 'Unscramble Machine'), ('Labeling 2', 'Labeling 2'), 
		('Filling Machine', 'Filling Machine'),], 'Tipe Laporan', copy=False)
	another_note = fields.Text(string='Another Awesome Notes', copy=False,
		default=""" * Condition OK means : clean, no straching sound, in a good shape
			* Machine stop under 30 min ditulis pada minor breakdown (Form Efficiency)
			* SPV melakukan tanda tangan bila mereview form """)
	note = fields.Char(string='Notes')
	date = fields.Date(string='Tanggal', default=fields.Date.today(), copy=False)
	okp_id = fields.Many2one('mrp.okp',string='OKP',)
	release_date = fields.Date(string='Revision Date')
	product_id = fields.Many2one('product.product',string='Product',)
	no_urut_bo = fields.Char(string='No Urut BO', size=2)
	# batch_id = fields.Many2one('source.model.name',string='Field Label',)

	# * GENERAL REPORT
	preparation = fields.Float(string='Preparation')
	total_breakdown = fields.Float(string='Total Breakdown')
	running_hours = fields.Float(string='Running Hours')
	total_reject_produk = fields.Float(string='Total Reject Produk')
	total_reject_carton = fields.Float(string='Total Reject Carton')
	total_output = fields.Float(string='Total Output')
	no_bo = fields.Char(string='No. BO')
	variant = fields.Char(string='Variant')
	start_aktual = fields.Char(string='Start Aktual')
	finish_aktual = fields.Char(string='Finish Aktual')
	start_pallet = fields.Char(string='Start Pallet')
	finish_pallet = fields.Char(string='Finish Pallet')

	# * PRODUCTION NOTES
	date = fields.Date(string='Tanggal')
	dayofweek = fields.Selection([('0', 'Senin'), ('1', 'Selasa'),
		('2', 'Rabu'), ('3', 'Kamis'), ('4', 'Jumat'),
		('5', 'Sabtu'), ('6', 'Minggu')], 'Hari')
	shift = fields.Selection([('I', 'I'), ('II', 'II'),
		('III', 'III')], 'Shift')
	team = fields.Selection([('A', 'A'), ('B', 'B'),
		('C', 'C'), ('D', 'D')], 'Team', default='A')
	packaging = fields.Selection([('80', '80'), ('100', '100'),
		('140', '140'), ('130', '130'), ('180', '180')], 'Kemasan (ml)', default='80')
	line_machine = fields.Selection([('A', 'A'), ('B', 'B'),
		('C', 'C')], 'Line Machine', default='A')


	# Notes
	general_check_notes = fields.Text(string='Notes',)
	cip_notes = fields.Text(string='Notes',)
	# parameter_mesin_notes = fieldste


	# Checked
	leader_check = fields.Boolean(string='Leader Check',)
	leader_need_check = fields.Boolean(string='Leader Need Check',compute='_compute_leader_need_check')
	operator = fields.Char(string='Operator',)
	leader = fields.Char(string='Leader',)
	editable = fields.Boolean(string='Editable', compute='_user_can_edit', default=True)

	def _user_can_edit(self):
		for rec in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and rec.state == 'done':
				rec.editable = True
			elif rec.state in ('draft','in_progress'):
				rec.editable = True
			else:
				rec.editable = False

	def name_get(self):
		res = []
		for rec in self:
			name = "[{}] {}".format(str(rec.no_urut_bo), str(rec.name)) if rec.no_urut_bo else str(rec.name)
			res.append((rec.id, name))
		return res


	def _compute_leader_need_check(self):
		self.leader_need_check = True if self.state == 'done' and not self.leader_check else False
		
	def action_leader_check(self):
		self.write({'leader_check' : True})

	def action_submit(self):
		return self.write({'state' : 'in_progress'})

	def action_approve_template(self):
		self.write({'state' : 'model', 
					'revision' : self.revision + 1, 
					# 'release_date' : fields.Date.context_today(self)
					})

	def action_done(self):
		return self.write({'state' : 'done'})

	def unlink(self):
		for rec in self:
			if rec.state not in ('draft', 'draft_model'):
				raise ValidationError(_("Data Tidak Dapat Dihapus!"))
		return super(KmiDailyReport, self).unlink()

	# @api.onchange('date', 'dayofweek')
	# def _onchange_date(self):
	#     if self.date:
	#         self.dayofweek = str(self.date.weekday())
	
	# def action_post(self):
	#     pass
	
	def action_cancel(self):
	    return self.write({'state': 'cancel'})
	
	def action_draft_model(self):
	    return self.write({'state': 'draft_model'})

	# def action_draft(self):
	#     return self.write({'state': 'draft'})

class kmiBatchReport(models.AbstractModel):
	_name = 'kmi.batch.report'
	_description = 'Line Batch Report'

	batch_number = fields.Char('No BO / Batch')
	product_id = fields.Many2one('product.product', string='Product Name')
	start_coding = fields.Float('Start Coding Btl')
	end_coding = fields.Float('Finish Coding Btl')
	output_batch = fields.Char(string='Output/Batch (btl)')
	reject_batch = fields.Float(string='Reject/Batch (btl)')

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state in ('draft','in_progress'):
				line.editable = True
			else:
				line.editable = False



class KmiGeneralCheck(models.AbstractModel):
	_name = 'kmi.general.checks'
	_description = 'Laporan Harian - General Check'

	# * GENERAL CHECKS (early shift checks)
	no = fields.Char(string='#',)
	name = fields.Char(string='Parameter')
	standard = fields.Char(string='Std')
	actual = fields.Char(string='Actual')
	param_group = fields.Char(string='Group Parameter')
	matching = fields.Boolean(string='Matching', copy=False)
	item = fields.Many2one('product.product', string='Item')
	start_vol = fields.Char('Start Vol')
	end_vol = fields.Char('End Vol')
	change_time = fields.Char('Change Time')
	type_operation = fields.Selection([
		('no', 'No'),
		('fix', 'Fixed'), 
		('between', 'Between'), 
		('>', '>'),
		('>=', '>='), 
		('<', '<'),
		('<=', '<='),
		],default='no', help="""
		* [No] Jika tidak membutuhkan STD sebagai pembanding
		* [Fixed] Hanya memiliki 1 nilai tetap selain nilai tersebut dinyatakan tidak sesuai
		* [Between] Memiliki 2 nilai angka yg dipisahkan dengan separator '-'
		* [>] Menggunakan simbol > dan nilai setelahnya adalah angka
		* [<] Menggunakan simbol < dan nilai setelahnya adalah angka
		* [>=] Menggunakan simbol >= dan nilai setelahnya adalah angka
		* [<=] Menggunakan simbol <= dan nilai setelahnya adalah angka
		""")

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state == 'in_progress':
				line.editable = True
			else:
				line.editable = False

	@api.onchange('actual')
	def onchange_actual(self):
		for line in self:
			line.check_standard_value()

	def check_standard_value(self):
		def isfloat(num):
			try:
				float(num)
				return True
			except ValueError:
				return False

		def raiseError():
			raise ValidationError(_('Masukkan Angka Sebagai Nilai Standard'))

		# for line in self:
		if self.type_operation == 'fix':
			self.matching = True if self.actual.casefold() == self.standard.casefold() else False
		elif self.type_operation == 'between':
			print('MASUK KE SINI?')
			if '-' not in self.standard:
				raise ValidationError(_('Separator Between Tidak Sesuai'))
			split = self.standard.split('-')
			if len(split) != 2:
				raise ValidationError(_('Nilai standard Untuk Between harus 2 nilai yang berbeda'))
			if any(isfloat(x) == False for x in split):
				raise ValidationError(_('Kedua nilai standard haruslah angka'))
			if not isfloat(self.actual):
				raise ValidationError(_('Masukkan angka sebagai actual'))
			std_morethan = float(split[0])
			std_lessthan = float(split[1])
			print(std_morethan, std_lessthan)
			# if float(self.actual) >= std_morethan and float(self.actual) <= std_lessthan:
			# 	print('MASUK??')
			self.matching = True if float(self.actual) >= std_morethan and float(self.actual) <= std_lessthan else False
		elif self.type_operation == '>':
			split = self.standard.split('>')
			std_value = float(split[1]) if isfloat(split[1]) else raiseError()
			if not isfloat(self.actual):
				raise ValidationError(_('Masukkan Angka Sebagai actual'))
			self.matching = True if float(self.actual) > std_value else False
		elif self.type_operation == '<':
			split = self.standard.split('<')
			std_value = float(split[1]) if isfloat(split[1]) else raiseError()
			if not isfloat(self.actual):
				raise ValidationError(_('Masukkan Angka Sebagai actual'))
			self.matching = True if float(self.actual) < std_value else False
		elif self.type_operation == '>=':
			split = self.standard.split('>=')
			std_value = float(split[1]) if isfloat(split[1]) else raiseError()
			if not isfloat(self.actual):
				raise ValidationError(_('Masukkan Angka Sebagai actual'))
			self.matching = True if float(self.actual) >= std_value else False
		elif self.type_operation == '<=':
			split = self.standard.split('<=')
			std_value = float(split[1]) if isfloat(split[1]) else raiseError()
			if not isfloat(self.actual):
				raise ValidationError(_('Masukkan Angka Sebagai actual'))
			self.matching = True if float(self.actual) <= std_value else False
		else:
			self.matching = True

class KmiParamsValue(models.AbstractModel):
	_name = 'kmi.params.value'
	_description = 'Parameter Value'

	note = fields.Text(string='Note')
	name = fields.Char(string='Parameter')
	check_time = fields.Char(string='Time Check')
	param_0 = fields.Char('0')
	param_1 = fields.Char('1')
	param_2 = fields.Char('2')
	param_3 = fields.Char('3')
	param_4 = fields.Char('4')
	param_5 = fields.Char('5')
	param_6 = fields.Char('6')
	param_7 = fields.Char('7')
	param_8 = fields.Char('8')
	param_9 = fields.Char('9')
	param_10 = fields.Char('10')
	param_11 = fields.Char('11')
	param_12 = fields.Char('12')
	param_13 = fields.Char('13')
	param_14 = fields.Char('14')
	param_15 = fields.Char('15')
	param_16 = fields.Char('16')
	check_time1 = fields.Char(string='Time Check 1')
	check_time2 = fields.Char(string='Time Check 2')
	check_time3 = fields.Char(string='Time Check 3')
	check_time4 = fields.Char(string='Time Check 4')

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state == 'in_progress':
				line.editable = True
			else:
				line.editable = False

class KmiMaterialUsage(models.AbstractModel):
	_name = 'kmi.material.usage'
	_description = 'PRODUCTION RECORD - MATERIAL/LABEL USAGE'

	# * PRODUCTION RECORD - MATERIAL/LABEL USAGE
	time_change = fields.Float(string='Time change')
	material_banded_6 = fields.Char(string='Banded 6')
	material_banded_2 = fields.Char(string='Banded 2')			
	material_single = fields.Char(string='Single')

	item_code = fields.Char(string='Item Code')
	fs_roll = fields.Float(string='First Stock - Roll')
	fs_kg = fields.Float(string='First Stock - Kg')
	start = fields.Float(string='Start')
	finish = fields.Float(string='Finish')
	in_qty = fields.Float(string='In')
	batch_code = fields.Char(string='Code Batch')
	out_qty = fields.Float(string='Out')
	reject_machine_qty = fields.Float(string='Reject Mesin/ manual')
	return_qty = fields.Float(string='Return')
	ss_join = fields.Float(string='Supplier Slice - Join')
	ss_actual = fields.Float(string='Supplier Slice - Actual')
	kmi_slice = fields.Float(string='KAMI Slice')
	conv_kg_roll = fields.Float(string='Konversi usage kg ke roll', default='1.0')
	reject_coding_qty = fields.Float(string='Reject Coding')
	reject_supplier_qty = fields.Float(string='Reject Supplier')
	last_stock = fields.Float(string='Last stock')

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state == 'in_progress':
				line.editable = True
			else:
				print('MASUK KE SINI?')
				line.editable = False

class KmiIncompatibilityNotes(models.AbstractModel):
	_name = 'kmi.incompatibility.notes'
	_description = 'CATATAN KETIDAKSESUAIAN SELAMA PROSES PRODUKSI'

	# * Major breakdown
	start = fields.Float(string='Start')
	finish = fields.Float(string='Finish')
	total = fields.Float(string='Total', compute='_compute_total')
	uraian_masalah = fields.Text(string='Uraian Masalah')
	# * Minor breakdown
	frekuensi = fields.Char(string='Frekuensi')
	status = fields.Char(string='Status')
	pic = fields.Char(string='PIC')

	@api.depends('start', 'finish')
	def _compute_total(self):
		for rec in self:
			rec.total = rec.finish - rec.start

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state == 'in_progress':
				line.editable = True
			else:
				line.editable = False

class kmiVerifyCoding(models.AbstractModel):
	_name = 'kmi.verify.coding'
	_description = 'VERIFIKASI CODING BODI'

	set_coding_by_qc = fields.Char('Setting Coding Bodi Botol')
	actual_coding = fields.Image('Actual Coding Bodi Botol', max_width=256, max_height=256)
	pic_produksi = fields.Char(string='PIC Produksi')
	jam_cetak_coding = fields.Float('Jam Cetak Coding')
	pic_qc = fields.Char(string='PIC QC')
	jam_verifikasi_coding = fields.Float('Jam Verifikasi Coding')
	status_verifikasi = fields.Char('Status Verifikasi')

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state == 'in_progress':
				line.editable = True
			else:
				line.editable = False
