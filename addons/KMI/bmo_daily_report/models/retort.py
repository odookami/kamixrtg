from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class KmiRetort(models.Model):
	_name = 'kmi.retort'
	_inherit = 'kmi.daily.report'

	active = fields.Boolean('Active', default='True')
	model_id = fields.Many2one('kmi.retort',string='Model',)

	batch = fields.Char('Batch')
	product_name = fields.Many2one('product.product' ,'Product Name')
	start = fields.Datetime('Start')
	finish = fields.Datetime('Finish')
	note = fields.Text('Notes')

	note_general = fields.Text('Note General Report')
	note_checks = fields.Text('Note General Checks')
	batch_1 = fields.Char(string='Batch 1',)
	batch_2 = fields.Char(string='Batch 2',)
	batch_3 = fields.Char(string='Batch 3',)
	batch_4 = fields.Char(string='Batch 4',)
	batch_note_1 = fields.Char(string='Batch Notes 1',)
	batch_note_2 = fields.Char(string='Batch Notes 2',)
	batch_note_3 = fields.Char(string='Batch Notes 3',)
	batch_note_4 = fields.Char(string='Batch Notes 4',)

	# One2many
	batch_line = fields.One2many('kmi.retort.batch.report', 
		'retort_id', string='Batch Line')
	checks_line = fields.One2many('kmi.retort.general.checks', 
		'retort_id', string='General Checks')
	prod_rec_line = fields.One2many('kmi.retort.params.value', 'retort_id', string='Production Record All')
	prod_rec_1_line = fields.One2many('kmi.retort.params.value', 'retort_id', string='Production Record 1', domain=[('group','=','1'), ])
	prod_rec_2_line = fields.One2many('kmi.retort.params.value', 'retort_id', string='Production Record 2', domain=[('group','=','2'), ])
	prod_rec_3_line = fields.One2many('kmi.retort.params.value', 'retort_id', string='Production Record 2', domain=[('group','=','3'), ])
	prod_rec_4_line = fields.One2many('kmi.retort.params.value', 'retort_id', string='Production Record 2', domain=[('group','=','4'), ])
	incompatibility_line = fields.One2many('kmi.retort.incompatibility.notes', 
		'retort_id', string='Catatan Proses Produksi')

	retort_note = fields.Text(string='Another Awesome Notes', copy=False,
		default=""" * Condition OK means : clean, no straching sound, in a good shape
		* Machine stop under 15 min ditulis pada minor breakdown
		* SPV melakukan tanda tangan bila mereview form
		* Range grafik chil go: 121˚C              , Benecol : 100˚C
		© = CCP """)
	
	def insert_production_record(self, batch_line):
		# print(values)
		if self.prod_rec_line:
			groups = self.prod_rec_line.mapped('group')
			existing_group = []
			for x in groups:
				existing_group.append(x) if x not in existing_group else ''
			if next_group > 2:
				raise ValidationError(_('Anda tidak dapat menambahkan lebih dari 3 batch ke transaksi ini'))
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
		values = \
			[batch.batch_number for batch in self.batch_line.filtered(lambda l: not l.start_coding and not l.end_coding and not l.output_batch and not l.reject_batch)] + \
			[check.name for check in self.checks_line.filtered(lambda l: not l.matching)]
		# 		+ [x.name for x in self.prod_rec_line.filtered(lambda l: not all([l.param_1, l.param_2, l.param_3, l.param_4, l.param_5, l.param_6]))]
		return values

	def check_null_value(self):
		null_values = self._get_null_values()
		if null_values:
			raise ValidationError(_('{} Belum Terisi Atau Belum Sesuai STD'.format(null_values[0])))
	
	def get_model(self):
		model = self.env['kmi.retort'].search([('state', '=', 'model')],limit=1)
		return model
	
	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		return super(KmiRetort, self).action_submit()
	
	def action_done(self):
		# self.check_null_value()
		return super(KmiRetort, self).action_done()
	
	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))
		self.write({
			'name' : model.name,
			'revision' : model.revision,
			'release_date' : model.release_date,
			'model_id' : model.id,
			'checks_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation}) for x in model.checks_line],
			# 'prod_rec_1_line' : [(0,0,{'name' : x.name, 'group' : '1'}) for x in model.prod_rec_line],
			# 'prod_rec_2_line' : [(0,0,{'name' : x.name, 'group' : '2'}) for x in model.prod_rec_line],
			# 'prod_rec_3_line' : [(0,0,{'name' : x.name, 'group' : '3'}) for x in model.prod_rec_line],
			# 'prod_rec_4_line' : [(0,0,{'name' : x.name, 'group' : '4'}) for x in model.prod_rec_line],
			})

class kmiBatchReport(models.Model):
	_name = 'kmi.retort.batch.report'
	_inherit = 'kmi.batch.report'

	retort_id = fields.Many2one('kmi.retort', 
		string='Batch Report Line', ondelete='cascade')
	prod_rec_line = fields.One2many('kmi.retort.params.value','batch_report_id',string='Retort Params',)
	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),
		('4', '4'),
		('5', '5'),
		('6', '6'),
		('7', '7'),
		('8', '8'),], string='Line Position')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.retort_id), default=True)

	prod_rec_created = fields.Boolean(string='Production Record Created',)
	def insert_production_record(self):
		# print(values)
		self.ensure_one()
		if self.retort_id.prod_rec_line:
			existing_group = self.retort_id.prod_rec_line.mapped('group')
			next_group = int(existing_group[len(existing_group) - 1]) + 1
			if next_group > 8:
				raise ValidationError(_('Anda tidak dapat menambahkan lebih dari 8 batch ke transaksi ini'))
			self.retort_id.write({
				'{}'.format('batch_'+ str(next_group)) : self.batch_number,
				'prod_rec_line' : [(0,0,{'name' : line.name, 'group' : str(next_group)}) for line in self.retort_id.model_id.prod_rec_line]
				})
			# print(next_group)
		else:
			self.retort_id.write({
				'batch_1' : self.batch_number,
				'prod_rec_line' : [(0,0,{'name' : line.name, 'group' : '1'}) for line in self.retort_id.model_id.prod_rec_line]
				})
		self.write({'prod_rec_created':True})

class KmiGeneralCheck(models.Model):
	_name = 'kmi.retort.general.checks'
	_inherit = 'kmi.general.checks'

	retort_id = fields.Many2one('kmi.retort', string='Retort')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.retort_id), default=True)

class KmiParamsValue(models.Model):
	_name = 'kmi.retort.params.value'
	_inherit = 'kmi.params.value'

	retort_id = fields.Many2one('kmi.retort', 
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
	batch_report_id = fields.Many2one('kmi.retort.batch.report',string='Batch Report',)
	param_17 = fields.Char('17')
	param_18 = fields.Char('18')
	param_19 = fields.Char('19')
	param_20 = fields.Char('20')
	param_21 = fields.Char('21')
	param_22 = fields.Char('22')
	param_23 = fields.Char('23')
	param_24 = fields.Char('24')
	param_25 = fields.Char('25')
	param_26 = fields.Char('26')
	param_27 = fields.Char('27')
	param_28 = fields.Char('28')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.retort_id), default=True)

class KmiIncompatibilityNotes(models.Model):
	_name = 'kmi.retort.incompatibility.notes'
	_inherit = 'kmi.incompatibility.notes'

	retort_id = fields.Many2one('kmi.retort', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.retort_id), default=True)