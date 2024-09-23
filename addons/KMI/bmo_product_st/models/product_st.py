# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class product_st(models.Model):
	_name = 'product.st'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Product ST'

	name = fields.Char(
		'Name', tracking=True
	)
	model_id = fields.Many2one('product.st',string='Model',)
	date = fields.Date(
		'Hari / Tanggal', default=fields.Date.today(), tracking=True
	)
	shift = fields.Selection([
		('I', 'I'),('II', 'II'),('III', 'III')], string='Shift', tracking=True
	)
	team = fields.Selection([
		('A','A'), ('B','B'), ('C','C'),], string='Team')
	product_id = fields.Many2one(
		'product.product', 'Nama Produk')
	okp_id = fields.Many2one(
		'mrp.okp', 'Okp', tracking=True)
	batch_id = fields.Many2one(
		'mrp.production', 'Batch')
	hal = fields.Char(
		'Hal', tracking=True
	)
	revisi = fields.Integer(
		'Revisi', default='0', tracking=True, copy=False,
	)
	revision_date = fields.Date(string='Revision Date', default=fields.Date.context_today)
	state = fields.Selection([
		('draft', 'Draft'),
		('in_progress', 'In Progres'),
		('done','Done'),
		# ('closed', 'Closed'),
		('draft_model', 'Draft'),
		('model', 'Model')], string='Status', default='draft', tracking=True, copy=False,
	)
	note = fields.Text(
		string='CATATAN')
	company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
		default=lambda self: self.env.company)
	ket = fields.Text(
		'Waktu pemeriksaan chilgo setiap 15 menit, benecol setiap 20 menit',
		default="""    
* Temp pasteurisasi untuk chilgo adalah 85, Benecol 90
** Temp produk oulet untuk chilgo maksimal 10, Benecol 27-31
*** SPV melakukan tanda tangan bila mereview form
**** OK jika tidak ditemukan adanya abnormalitas dari segi warna, aroma, rasa dan Foreign Matter
***** Ukuran fat globule ≥ 2 µm adalah ≤ 30% dari total pengamatan """)
	tekanan = fields.Text(
		'Tekanan chiller max. 1,5 bar', copy=False, 
		default="""Untuk chilgo, Chiller ON ketika suhu di sorage di atas  9 .""")
	operator = fields.Char(string='Operator',)
	leader = fields.Char(string='Leader',)

	suhu = fields.Char('Suhu')
	product_st_line = fields.One2many('product.st.line','product_st_id',string='Product ST', copy=True)
	preparation_ids = fields.One2many(
		'product.st.line', 'product_st_id', string='Preparation', tracking=True, domain=[('group', '=', '1')]
	)
	preheating_ids = fields.One2many(
		'product.st.line', 'product_st_id', string='Pre-Heating', tracking=True, domain=[('group', '=', '2')]
	)
	pasteurization_1_ids = fields.One2many(
		'product.st.line', 'product_st_id', string='Pasteurization 1', tracking=True, domain=[('group', '=', '301')]
	)
	pasteurization_2_ids = fields.One2many(
		'product.st.line', 'product_st_id', string='Pasteurization 2', tracking=True, domain=[('group', '=', '302')]
	)
	pasteurization_3_ids = fields.One2many(
		'product.st.line', 'product_st_id', string='Pasteurization 3', tracking=True, domain=[('group', '=', '303')]
	)
	pasteurization_4_ids = fields.One2many(
		'product.st.line', 'product_st_id', string='Pasteurization 4', tracking=True, domain=[('group', '=', '304')]
	)
	pasteurization_5_ids = fields.One2many(
		'product.st.line', 'product_st_id', string='Pasteurization 5', tracking=True, domain=[('group', '=', '305')]
	)
	quality_analysis_ids = fields.One2many(
		'product.st.line', 'product_st_id', string='Quality Analysis', tracking=True, domain=[('group', '=', '4')]
	)
	st_no_ids = fields.One2many(
		'product.st.line', 'st_no_id', string='ST No.', domain=[('group', '=', '5')]
	)
	page_a_title = fields.Char(string='Page A Title',)
	page_b_title = fields.Char(string='Page B Title',)
	page_c_title = fields.Char(string='Page C Title',)
	page_d_title = fields.Char(string='Page D Title',)
	page_e_title = fields.Char(string='Page E Title',)
	leader_check = fields.Boolean(string='Leader Check',)
	leader_need_check = fields.Boolean(string='Leader Need Check',compute='_compute_leader_need_check')

	editable = fields.Boolean(string='Editable', compute='_user_can_edit', default=True)

	def _user_can_edit(self):
		for rec in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and rec.state == 'done':
				rec.editable = True
			elif rec.state in ('draft', 'in_progress'):
				rec.editable = True
			else:
				rec.editable = False

	def action_approve_template(self):
		self.write({'state' : 'model', 'revisi' : self.revisi + 1})

	def _compute_leader_need_check(self):
		self.leader_need_check = True if self.state == 'done' and not self.leader_check else False
		
	def action_leader_check(self):
		self.write({'leader_check' : True})
		
	def name_get(self):
		res = []
		for rec in self:
			name = "[{}] {}".format(str(rec.batch_id.number_ref), str(rec.name)) if rec.batch_id else str(rec.name)
			res.append((rec.id, name))
		return res
	
	def check_null_value(self):
		null_value = self.product_st_line.filtered(lambda l:(l.line_type == 'quality') and not l.matching)
		print(null_value)
		if null_value:
			raise ValidationError(_('Nomor {} - {} Belum Terisi Atau Belum Sesuai STD'.format(null_value[0].number, null_value[0].name)))

	def action_done(self):
		self.check_null_value()
		return self.write({'state' : 'done'})
	
	def action_model(self):
		for rec in self:
			rec.state = "model"
	
	def action_draft(self):
		for rec in self:
			rec.state = "draft"

	@api.onchange('batch_id')
	def _onchange_okp(self):
		# domain = {}
		if self.batch_id:
			self.okp_id = self.batch_id.okp_id.id
			self.product_id = self.batch_id.product_id.id
			# domain = {'batch_id': [('id', 'in', self.batch_id.batch_mo_line.ids)], 'product_id': [('id', 'in', self.okp_id.batch_mo_line.product_id.ids)]}
		# return {'domain': domain}

	def get_model(self):
		model = self.env['product.st'].search([('product_id', '=', self.product_id.id), ('state', '=', 'model')],limit=1)
		return model
	
	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		self.write({'state' : 'in_progress'})
	
	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))

		self.write({
			'name' : model.name,
			'revisi' : model.revisi,
			'revision_date' : model.revision_date,
			'model_id' : model.id,
			'ket' : model.ket,
			'page_a_title' : model.page_a_title,
			'page_b_title' : model.page_b_title,
			'page_c_title' : model.page_c_title,
			'page_d_title' : model.page_d_title,
			'page_e_title' : model.page_e_title,
			'preparation_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'group' : x.group, 'line_type' : x.line_type}) for x in model.preparation_ids],
			'pasteurization_1_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'group' : x.group, 'line_type' : x.line_type}) for x in model.pasteurization_1_ids],
			'pasteurization_2_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'group' : x.group, 'line_type' : x.line_type}) for x in model.pasteurization_2_ids],
			'pasteurization_3_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'group' : x.group, 'line_type' : x.line_type}) for x in model.pasteurization_3_ids],
			'pasteurization_4_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'group' : x.group, 'line_type' : x.line_type}) for x in model.pasteurization_4_ids],
			'pasteurization_5_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'group' : x.group, 'line_type' : x.line_type}) for x in model.pasteurization_5_ids],
			'preheating_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'group' : x.group, 'line_type' : x.line_type}) for x in model.preheating_ids],
			# 'pasteurization_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'product_st_id' : self.id}) for x in model.pasteurization_ids],
			'quality_analysis_ids' : [(0,0,{'number': x.number, 'name' : x.name, 'unit':x.unit, 'type_operation':x.type_operation, 'std' : x.std, 'group' : x.group, 'line_type' : x.line_type}) for x in model.quality_analysis_ids],
		})

class product_st_line(models.Model):
	_name = 'product.st.line'
	_description = 'Product ST Line'
	_order = 'number'

	number = fields.Integer(
		'No', copy=True)
	name = fields.Char(
		'Uraian Kegiatan', copy=True)
	unit = fields.Char(
		'Unit', copy=True)
	std = fields.Char(
		'Parameter', copy=True)
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

	matching = fields.Boolean(string='Matching')
	editable = fields.Boolean(string='Is Editable',compute='_user_can_edit')
	line_type = fields.Selection([
		('production', 'Production'),
		('quality', 'Quality'),], string='Line Type', default='production', copy=True)
	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('301', '301'),('302', '302'),('303', '303'),('304', '304'),
		('4', '4'),
		('5', '5'),
		], string='Group', copy=True)

	actual = fields.Char(
		'Actual')
	actual_0 = fields.Char(
		'Actual(0)')
	actual_15 = fields.Char(
		'Actual(15)')
	actual_30 = fields.Char(
		'Actual(30)')
	actual_45 = fields.Char(
		'Actual(45)')
	actual_60 = fields.Char(
		'Actual(60)')
	st_no = fields.Char(
		'ST No.')
	suhu_jam_2 = fields.Char(
		'2')
	suhu_jam_4 = fields.Char(
		'4')
	suhu_jam_6 = fields.Char(
		'6')
	suhu_jam_8 = fields.Char(
		'8')
	suhu_jam_10 = fields.Char(
		'10')
	suhu_jam_12 = fields.Char(
		'12')
	suhu_jam_14 = fields.Char(
		'14')
	suhu_jam_16 = fields.Char(
		'16')
	suhu_jam_18 = fields.Char(
		'18')
	suhu_jam_20 = fields.Char(
		'20')
	suhu_jam_22 = fields.Char(
		'22')
	suhu_jam_24 = fields.Char(
		'24')
	suhu_jam_26 = fields.Char(
		'26')
	suhu_jam_28 = fields.Char(
		'28')
	suhu_jam_30 = fields.Char(
		'30')
	pasteur_start = fields.Float(string='Start',)
	pasteur_finish = fields.Float(string='Finish',)

	product_st_id = fields.Many2one('product.st', string='Product ST',)
	preparation_id = fields.Many2one('product.st', string='Preparation Lines',)
	pasteurization_1_id = fields.Many2one('product.st', string='Pasteurization 1 Lines',)
	pasteurization_2_id = fields.Many2one('product.st', string='Pasteurization 2 Lines',)
	pasteurization_3_id = fields.Many2one('product.st', string='Pasteurization 3 Lines',)
	pasteurization_4_id = fields.Many2one('product.st', string='Pasteurization 4 Lines',)
	pasteurization_5_id = fields.Many2one('product.st', string='Pasteurization 5 Lines',)
	preheating_id = fields.Many2one('product.st', string='Pre-Heating Lines',)
	quality_analysis_id = fields.Many2one('product.st', string='Quality Analysis Lines',)
	st_no_id = fields.Many2one('product.st', string='ST No Lines',)

	# @api.onchange

	# @api.depends('product_st_id.state')
	def _user_can_edit(self):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and line.product_st_id.state == 'done':
				line.editable = True
			elif line.product_st_id.state == 'in_progress':
				line.editable = True
			else:
				line.editable = False

	def check_all_value(self):
		self.ensure_one()
		values = [self.actual,self.pasteur_start, self.pasteur_finish]
		return True if any(x for x in values) else False

	# @api.depends('actual', 'actual_0', 'actual_15', 'actual_30', 'actual_45', 'actual_60', )
	def check_standard_value(self):
		def isfloat(num):
			try:
				float(num)
				return True
			except ValueError:
				return False

		def raiseError():
			raise ValidationError(_('Masukkan Angka Sebagai Nilai STD'))

		# print('------------------- CHECK STANDARD VALUE ---------------------')

		for line in self:
			values = [line.actual_0, line.actual_15, line.actual_30, line.actual_45, line.actual_60,line.pasteur_start,line.pasteur_finish]
			if line.type_operation == 'fix':
				if line.actual:
					line.matching = True if line.actual.casefold() == line.std.casefold() else False
				elif any(x for x in values):
					line.matching = True if all(x.casefold() == line.std.casefold() for x in values) else False
			elif line.type_operation == 'between':
				if '-' not in line.std:
					raise ValidationError(_('Separator Between Tidak Sesuai'))
				split = line.std.split('-')
				if len(split) != 2:
					raise ValidationError(_('Nilai STD Untuk Between harus 2 nilai yang berbeda'))
				if any(isfloat(x) == False for x in split):
					raise ValidationError(_('Kedua nilai STD haruslah angka'))
				if not isfloat(line.actual):
					raise ValidationError(_('Masukkan angka sebagai value'))
				std_morethan = float(split[0])
				std_lessthan = float(split[1])
				if line.actual:
					line.matching = True if float(line.actual) >= std_morethan and float(line.actual) <= std_lessthan else False
				elif any(x for x in values):
					line.matching = True if all(float(x) >= std_morethan and float(x) <= std_lessthan for x in values) else False
			elif line.type_operation == '>':
				split = line.std.split('>')
				std_value = float(split[1]) if isfloat(split[1]) else raiseError()
				if not isfloat(line.actual):
					raise ValidationError(_('Masukkan Angka Sebagai Value'))
				if line.actual:
					line.matching = True if float(line.actual) > std_value else False
				elif any(x for x in values):
					line.matching = True if all(float(value) > std_value for value in values) else False
			elif line.type_operation == '<':
				split = line.std.split('<')
				std_value = float(split[1]) if isfloat(split[1]) else raiseError()
				if not isfloat(line.actual):
					raise ValidationError(_('Masukkan Angka Sebagai Value'))
				if line.actual:
					line.matching = True if float(line.actual) < std_value else False
				elif any(x for x in values):
					line.matching = True if all(float(value) < std_value for value in values) else False
				
			elif line.type_operation == '>=':
				split = line.std.split('>=')
				std_value = float(split[1]) if isfloat(split[1]) else raiseError()
				if not isfloat(line.actual):
					raise ValidationError(_('Masukkan Angka Sebagai Value'))
				if line.actual:
					line.matching = True if float(line.actual) >= std_value else False
				elif any(x for x in values):
					line.matching = True if all(float(value) >= std_value for value in values) else False
				
			elif line.type_operation == '<=':
				split = line.std.split('<=')
				std_value = float(split[1]) if isfloat(split[1]) else raiseError()
				if not isfloat(line.actual):
					raise ValidationError(_('Masukkan Angka Sebagai Value'))
				if line.actual:
					line.matching = True if float(line.actual) <= std_value else False
				elif any(x for x in values):
					line.matching = True if all(float(value) <= std_value for value in values) else False
			else:
				if line.actual:
					line.matching = True
				else:
					print('masuk sini?')
					line.matching = True if any(x for x in values) else False
				

	@api.onchange('actual','pasteur_start','pasteur_finish')
	def _onchange_actual_value(self):
		for line in self:
			line.check_standard_value()

	# @api.onchange('actual_0')
	# def _onchange_actual_0_value(self):
	# 	for line in self:
	# 		line.check_standard_value(line.actual_0)

	# @api.onchange('actual_15')
	# def _onchange_actual_15_value(self):
	# 	for line in self:
	# 		line.check_standard_value(line.actual_15)

	# @api.onchange('actual_30')
	# def _onchange_actual_30_value(self):
	# 	for line in self:
	# 		line.check_standard_value(line.actual_30)

	# @api.onchange('actual_45')
	# def _onchange_actual_45_value(self):
	# 	for line in self:
	# 		line.check_standard_value(line.actual_45)

	# @api.onchange('actual_60')
	# def _onchange_actual_60_value(self):
	# 	for line in self:
	# 		line.check_standard_value(line.actual_60)

