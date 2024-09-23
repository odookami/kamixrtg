# -*- coding: utf-8 -*-

import io
import os
import base64
from openpyxl import load_workbook
from openpyxl.styles import NamedStyle
from dateutil import relativedelta
from datetime import date, datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re



class kmi_dumping(models.Model):
	_name = 'kmi.dumping'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Dumping'
	_order = 'revisi desc'

	active = fields.Boolean('Active', default='True')
	name = fields.Char(
		'Name', tracking=True, default='New'
	)
	date = fields.Date(
		'Hari / Tanggal', default=fields.Date.context_today, tracking=True
	)
	shift = fields.Selection([
		('I', 'I'),('II', 'II'),('III', 'III')], string='Shift', tracking=True
	)
	hal = fields.Char(
		'Hal', tracking=True
	)
	revisi = fields.Integer(
		'Revisi', default='0', tracking=True
	)
	revision_date = fields.Date(string='Revision Date')
	tolerance_precision = fields.Float(string='Tolerance Row Report',)
	product_id = fields.Many2one(
		"product.product", string="Product")
	banded = fields.Selection([('banded_6', 'Banded 6'), ('single', 'Single')],
		string='Banded', default='banded_6'
	)
	user_id = fields.Many2one(
		'res.users', string='User Produksi'
	)
	user_qc_id = fields.Many2one(
		'res.users', string='User Quality Control'
	)
	page_1_title = fields.Char(string='Page 1 Title',)
	page_2_title = fields.Char(string='Page 2 Title',)
	page_3_title = fields.Char(string='Page 3 Title',)
	page_4_title = fields.Char(string='Page 4 Title',)
	page_5_title = fields.Char(string='Page 5 Title',)
	page_6_title = fields.Char(string='Page 6 Title',)
	page_7_title = fields.Char(string='Page 7 Title',)
	page_8_title = fields.Char(string='Page 8 Title',)
	page_qa_title = fields.Char(string='Page QA Title',)
	company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
		default=lambda self: self.env.company
	)
	state = fields.Selection([
		('draft', 'Draft'),
		('in_progress', 'In Progres'),
		('done','Done'),
		# ('closed', 'Closed'),
		('draft_model', 'Draft'),
		('model', 'Model')], string='Status', default='draft', tracking=True, copy=False,
	)
	model_id = fields.Many2one('kmi.dumping',string='Model Template',)
	kmp_dumping_line = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Dumping Line', copy=True
	)
	page_1_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 1', tracking=True, domain=[('group', '=', '1')]
	)
	page_2_01_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 1', tracking=True, domain=[('group', '=', '201')]
	)
	page_2_02_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 2', tracking=True, domain=[('group', '=', '202')]
	)
	page_2_03_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 3', tracking=True, domain=[('group', '=', '203')]
	)
	page_2_04_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 4', tracking=True, domain=[('group', '=', '204')]
	)
	page_2_05_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 5', tracking=True, domain=[('group', '=', '205')]
	)
	page_2_06_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 6', tracking=True, domain=[('group', '=', '206')]
	)
	page_2_07_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 7', tracking=True, domain=[('group', '=', '207')]
	)
	page_2_08_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 8', tracking=True, domain=[('group', '=', '208')]
	)
	page_2_09_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 9', tracking=True, domain=[('group', '=', '209')]
	)
	page_2_10_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 10', tracking=True, domain=[('group', '=', '210')]
	)
	page_2_11_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 2 11', tracking=True, domain=[('group', '=', '211')]
	)
	page_3_01_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 3 1', tracking=True, domain=[('group', '=', '301')]
	)
	page_3_02_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 3 2', tracking=True, domain=[('group', '=', '302')]
	)
	page_3_03_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 3 3', tracking=True, domain=[('group', '=', '303')]
	)
	page_3_04_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 3 4', tracking=True, domain=[('group', '=', '304')]
	)
	page_4_01_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 4', tracking=True, domain=[('group', '=', '4')]
	)
	page_5_01_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 5', tracking=True, domain=[('group', '=', '5')]
	)
	page_6_01_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 6', tracking=True, domain=[('group', '=', '6')]
	)
	page_7_01_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 7', tracking=True, domain=[('group', '=', '7')]
	)
	page_8_01_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Page 8', tracking=True, domain=[('group', '=', '8')]
	)
	page_qa_ids = fields.One2many(
		'kmi.dumping.line', 'dumping_id', string='Quality Analysis', tracking=True, domain=[('group', '=', 'qa')]
	)

	notes = fields.Text(
		'Keterangan'
	)
	ket = fields.Text(
		'Keterangan', copy=True,
		default="""    
* Bila terjadi ketidak sesuaian segera info shift leader
* Cek terlebih dahulu semua peralatan proses, jalur dan sistem pada panel HMI apabila akan memulai MIXING lagi setelah melakukan proses CIP """)
	operator = fields.Char(string='Operator',)
	leader = fields.Char(string='Leader',)
	# shift_leader = fields.Selection([
	# 	('shift leader', 'Shift Leader'),('supervisor', 'Supervisor')], string='Shift leader/Supervisor:', tracking=True
	# )

	okp_id = fields.Many2one('mrp.okp',string='OKP',)
	mo_id = fields.Many2one('mrp.production',string='Batch',)
	leader_check = fields.Boolean(string='Leader Check',)
	leader_need_check = fields.Boolean(string='Leader Need Check',compute='_compute_leader_need_check')

	editable = fields.Boolean(string='Editable', compute='_user_can_edit', default=True)

	def _user_can_edit(self):
		for rec in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and rec.state == 'done':
				rec.editable = True
			elif rec.state in ('draft','in_progress'):
				rec.editable = True
			else:
				rec.editable = False

	def _compute_leader_need_check(self):
		self.leader_need_check = True if self.state == 'done' and not self.leader_check else False
		
	def action_leader_check(self):
		self.write({'leader_check' : True})

	def name_get(self):
		res = []
		for rec in self:
			name = "[{}] {}".format(str(rec.mo_id.number_ref), str(rec.name)) if rec.mo_id else str(rec.name)
			res.append((rec.id, name))
		return res

	def action_approve_template(self):
		self.write({'state' : 'model', 'revisi' : self.revisi + 1})

	@api.onchange('mo_id')
	def _onchange_mo_id(self):
		self.okp_id = self.product_id = False
		if self.mo_id:
			self.write({'okp_id' : self.mo_id.okp_id.id, 'product_id' : self.mo_id.product_id.id})

	def check_null_value(self):
		null_value = self.kmp_dumping_line.filtered(lambda l:(not l.value or not l.matching) and l.line_type == 'quality')
		print(null_value)
		if null_value:
			raise ValidationError(_('Nomor {} - {} Belum Terisi Atau Belum Sesuai STD'.format(null_value[0].number, null_value[0].name)))

	def action_release(self):
		self.check_null_value()
		self.write({'state' : 'done'})
		
	def action_submit(self):
		model = self.get_model()
		self.kmp_dumping_line.unlink()
		self.load_templates(model)
		self.write({'state' : 'in_progress'})

	def get_model(self):
		model = self.env['kmi.dumping'].search([('product_id', '=', self.product_id.id), ('state', '=', 'model')],limit=1)
		return model

	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))
		# self.kmi_dumping_line.unlink()
		self.write({
			'name' : model.name,
			'revisi' : model.revisi,
			'revision_date' : model.revision_date,
			'model_id' : model.id,
			'tolerance_precision' : model.tolerance_precision,
			'page_1_title' : model.page_1_title,
			'page_2_title' : model.page_2_title,
			'page_3_title' : model.page_3_title,
			'page_4_title' : model.page_4_title,
			'page_5_title' : model.page_5_title,
			'page_6_title' : model.page_6_title,
			'page_7_title' : model.page_7_title,
			'page_8_title' : model.page_8_title,
			'page_qa_title' : model.page_qa_title,
			'kmp_dumping_line' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'std' : x.std, 'type_operation' : x.type_operation, 'line_type' : x.line_type, 'group' : x.group}) for x in model.kmp_dumping_line]
			})

	def autofill(self):
		self.kmp_dumping_line.autofillvalue()

	datafile = fields.Binary(string='Data File',attachment=True,)
	filename = fields.Char(string='FileName',)
		

class kmi_dumping_line(models.Model):
	_name = 'kmi.dumping.line'
	_description = 'Dumping Line'
	_order = 'number asc'

	number = fields.Integer('No', copy=True, )
	name = fields.Char('Proses Produksi', copy=True)
	unit = fields.Char(string='Unit', copy=True)
	std = fields.Char(string='STD', copy=True)
	value = fields.Char(string='Value', copy=True)
	matching = fields.Boolean(string='Matching', copy=False)
	editable = fields.Boolean(string='Is Editable',compute='_user_can_edit')
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
	remark = fields.Char(string='Remark', copy=True)
	line_type = fields.Selection([
		('production', 'Production'),
		('quality', 'Quality'),], string='Line Type', default='production', copy=True)

	group = fields.Selection([
		('1', '1'),
		('201', '201'),('202', '202'),('203', '203'),('204', '204'),('205', '205'),('206', '206'),('207', '207'),('208', '208'),('209', '209'),('210', '210'),('211', '211'),
		('301', '301'),('302', '302'),('303', '303'),('304', '304'),
		('4', '4'),
		('5', '5'),
		('6', '6'),
		('7', '7'),
		('8', '8'),
		('qa', 'QA'),
		], string='Group', copy=True)

	dumping_id = fields.Many2one('kmi.dumping',string='Dumping ID',)

	page_1_id = fields.Many2one(
		'kmi.dumping', string='Page 1 1', 
	)
	page_2_01_id = fields.Many2one(
		'kmi.dumping', string='Page 2 1', 
	)
	page_2_02_id = fields.Many2one(
		'kmi.dumping', string='Page 2 2', 
	)
	page_2_03_id = fields.Many2one(
		'kmi.dumping', string='Page 2 3', 
	)
	page_2_04_id = fields.Many2one(
		'kmi.dumping', string='Page 2 4', 
	)
	page_2_05_id = fields.Many2one(
		'kmi.dumping', string='Page 2 5', 
	)
	page_2_06_id = fields.Many2one(
		'kmi.dumping', string='Page 2 6', 
	)
	page_2_07_id = fields.Many2one(
		'kmi.dumping', string='Page 2 7', 
	)
	page_2_08_id = fields.Many2one(
		'kmi.dumping', string='Page 2 8', 
	)
	page_2_09_id = fields.Many2one(
		'kmi.dumping', string='Page 2 9', 
	)
	page_2_10_id = fields.Many2one(
		'kmi.dumping', string='Page 2 10', 
	)
	page_2_11_id = fields.Many2one(
		'kmi.dumping', string='Page 2 11', 
	)
	page_3_01_id = fields.Many2one(
		'kmi.dumping', string='Page 3 1', 
	)
	page_3_02_id = fields.Many2one(
		'kmi.dumping', string='Page 3 2', 
	)
	page_3_03_id = fields.Many2one(
		'kmi.dumping', string='Page 3 3', 
	)
	page_3_04_id = fields.Many2one(
		'kmi.dumping', string='Page 3 4', 
	)
	page_4_01_id = fields.Many2one(
		'kmi.dumping', string='Page 4 1 ', 
	)
	page_5_01_id = fields.Many2one(
		'kmi.dumping', string='Page 5 1', 
	)
	page_6_01_id = fields.Many2one(
		'kmi.dumping', string='Page 6 1', 
	)
	page_7_01_id = fields.Many2one(
		'kmi.dumping', string='Page 7 1', 
	)
	page_8_01_id = fields.Many2one(
		'kmi.dumping', string='Page 8 1', 
	)
	page_qa_id = fields.Many2one(
		'kmi.dumping', string='Page QA', 
	)

	def _user_can_edit(self):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and line.dumping_id.state == 'done':
				line.editable = True
			elif line.dumping_id.state == 'in_progress':
				line.editable = True
			else:
				line.editable = False

	def check_standard_value(self):
		def isfloat(num):
			try:
				float(num)
				return True
			except ValueError:
				return False

		def raiseError():
			raise ValidationError(_('Masukkan Angka Sebagai Nilai STD'))

		# for line in self:
		if self.type_operation == 'fix':
			self.matching = True if self.value.casefold() == self.std.casefold() else False
		elif self.type_operation == 'between':
			print('MASUK KE SINI?')
			if '-' not in self.std:
				raise ValidationError(_('Separator Between Tidak Sesuai'))
			split = self.std.split('-')
			if len(split) != 2:
				raise ValidationError(_('Nilai STD Untuk Between harus 2 nilai yang berbeda'))
			if any(isfloat(x) == False for x in split):
				raise ValidationError(_('Kedua nilai STD haruslah angka'))
			if not isfloat(self.value):
				raise ValidationError(_('Masukkan angka sebagai value'))
			std_morethan = float(split[0])
			std_lessthan = float(split[1])
			self.matching = True if float(self.value) >= std_morethan and float(self.value) <= std_lessthan else False
		elif self.type_operation == '>':
			split = self.std.split('>')
			std_value = float(split[1]) if isfloat(split[1]) else raiseError()
			if not isfloat(self.value):
				raise ValidationError(_('Masukkan Angka Sebagai Value'))
			self.matching = True if float(self.value) > std_value else False
		elif self.type_operation == '<':
			split = self.std.split('<')
			std_value = float(split[1]) if isfloat(split[1]) else raiseError()
			if not isfloat(self.value):
				raise ValidationError(_('Masukkan Angka Sebagai Value'))
			self.matching = True if float(self.value) < std_value else False
		elif self.type_operation == '>=':
			split = self.std.split('>=')
			std_value = float(split[1]) if isfloat(split[1]) else raiseError()
			if not isfloat(self.value):
				raise ValidationError(_('Masukkan Angka Sebagai Value'))
			self.matching = True if float(self.value) >= std_value else False
		elif self.type_operation == '<=':
			split = self.std.split('<=')
			std_value = float(split[1]) if isfloat(split[1]) else raiseError()
			if not isfloat(self.value):
				raise ValidationError(_('Masukkan Angka Sebagai Value'))
			self.matching = True if float(self.value) <= std_value else False
		else:
			self.matching = True


	@api.onchange('value')
	def onchange_value(self):
		for line in self:
			line.check_standard_value()

	def autofillvalue(self):
		for line in self:
			if line.type_operation in ('fix','no'):
				line.value = 'TES'
			elif line.type_operation == 'between':
				split = line.std.split('-')
				line.value = split[0]
			elif line.type_operation in ('>', '<'):
				split = re.split('>|<',line.std)
				line.value = split[1]
			elif line.type_operation in ('>=', '<='):
				split = re.split('>=|<=',line.std)
				line.value = split[1]
			else:
				line.value = 'TIDAK ADA STD'
			line.matching=True


		url = content + download



	# ('no', '-'),
	# 	('fix', 'Fixed'), 
	# 	('between', 'Between'), 
	# 	('>', 'More Than'), 
	# 	('<', 'Less Than')

	# 	print(True if all(isinstance(x,float) for x in tipe) else False)