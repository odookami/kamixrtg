# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class KmiUnloader(models.Model):
	_name = 'kmi.unloader'
	_inherit = 'kmi.daily.report'

	active = fields.Boolean('Active', default='True')
	model_id = fields.Many2one('kmi.unloader',string='Model',)

	unloader_note = fields.Text(string='Important Note',
		default="""
		* Condition OK means : clean, no straching sound, in a good shape
		* Machine stop under 30 min ditulis pada minor breakdown (Form Efficiency)
		""")

	note_checks = fields.Text('Note General Checks')
	batch_1 = fields.Char(string='Batch 1',)
	batch_2 = fields.Char(string='Batch 2',)
	batch_3 = fields.Char(string='Batch 3',)
	batch_4 = fields.Char(string='Batch 4',)
	batch_5 = fields.Char(string='Batch 5',)
	batch_6 = fields.Char(string='Batch 6',)
	batch_7 = fields.Char(string='Batch 7',)
	batch_8 = fields.Char(string='Batch 8',)
	batch_note_1 = fields.Char(string='Batch Notes 1',)
	batch_note_2 = fields.Char(string='Batch Notes 2',)
	batch_note_3 = fields.Char(string='Batch Notes 3',)
	batch_note_4 = fields.Char(string='Batch Notes 4',)
	batch_note_5 = fields.Char(string='Batch Notes 5',)
	batch_note_6 = fields.Char(string='Batch Notes 6',)
	batch_note_7 = fields.Char(string='Batch Notes 7',)
	batch_note_8 = fields.Char(string='Batch Notes 8',)
	model_id = fields.Many2one('kmi.unloader',string='Model',)
	total_reject_produk = fields.Float(string='Total Reject Produk', compute='_compute_total_reject')
	# One2many
	batch_line = fields.One2many('kmi.unloader.batch.report', 'unloader_id', string='Batch Line')
	checks_line = fields.One2many('kmi.unloader.general.checks', 'unloader_id', string='General Checks')
	prod_rec_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record All')
	prod_rec_1_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record 1', domain=[('group','=','1'), ])
	prod_rec_2_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record 2', domain=[('group','=','2'), ])
	prod_rec_3_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record 3', domain=[('group','=','3'), ])
	prod_rec_4_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record 4', domain=[('group','=','4'), ])
	prod_rec_5_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record 5', domain=[('group','=','5'), ])
	prod_rec_6_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record 6', domain=[('group','=','6'), ])
	prod_rec_7_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record 7', domain=[('group','=','7'), ])
	prod_rec_8_line = fields.One2many('kmi.unloader.params.value', 'unloader_id', string='Production Record 8', domain=[('group','=','8'), ])
	incompatibility_line = fields.One2many('kmi.unloader.incompatibility.notes', 'unloader_id', string='Catatan Proses Produksi')
	
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
		values = [batch.batch_number for batch in self.batch_line.filtered(lambda l: not l.start_coding or not l.end_coding)]
			# + [x.name for x in self.checks_line.filtered(lambda l: not l.matching)]
			# + [x.name for x in self.prod_rec_line.filtered(lambda l: not all([l.param_1, l.param_2, l.param_3, l.param_4, l.param_5, l.param_6]))]

		return values

	def check_null_value(self):
		null_values = self._get_null_values()
		if null_values:
			raise ValidationError(_('{} Belum Terisi Atau Belum Sesuai STD'.format(null_values[0])))

	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		return super(KmiUnloader, self).action_submit()

	def action_done(self):
		# self.check_null_value()
		return super(KmiUnloader, self).action_done()

	def get_model(self):
		model = self.env['kmi.unloader'].search([('state', '=', 'model')],limit=1)
		# print(model)
		return model

	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))
		self.write({
			'name' : model.name,
			'revision' : model.revision,
			'release_date' : model.release_date,
			'model_id' : model.id,
			'checks_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation}) for x in model.checks_line],
			})

	@api.depends('batch_line')
	def _compute_total_reject(self):
		self.total_reject_produk = sum(x.reject_batch for x in self.batch_line)

class kmiBatchReport(models.Model):
	_name = 'kmi.unloader.batch.report'
	_inherit = 'kmi.batch.report'

	unloader_id = fields.Many2one('kmi.unloader', 
		string='Batch Report Line', ondelete='cascade')
	prod_rec_line = fields.One2many('kmi.unloader.params.value','batch_report_id',string='Unloader Params',)
	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),
		('4', '4'),
		('5', '5'),
		('6', '6'),
		('7', '7'),
		('8', '8'),], string='Line Position')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.unloader_id), default=True)
	prod_rec_created = fields.Boolean(string='Production Record Created',)

	def insert_production_record(self):
		# print(values)
		self.ensure_one()
		if self.unloader_id.prod_rec_line:
			existing_group = self.unloader_id.prod_rec_line.mapped('group')
			next_group = int(existing_group[len(existing_group) - 1]) + 1
			if next_group > 8:
				raise ValidationError(_('Anda tidak dapat menambahkan lebih dari 8 batch ke transaksi ini'))
			self.unloader_id.write({
				'{}'.format('batch_'+ str(next_group)) : self.batch_number,
				'prod_rec_line' : [(0,0,{'name' : line.name, 'group' : str(next_group)}) for line in self.unloader_id.model_id.prod_rec_line]
				})
			# print(next_group)
		else:
			self.unloader_id.write({
				'batch_1' : self.batch_number,
				'prod_rec_line' : [(0,0,{'name' : line.name, 'group' : '1'}) for line in self.unloader_id.model_id.prod_rec_line]
				})
		self.write({'prod_rec_created':True})

class KmiGeneralCheck(models.Model):
	_name = 'kmi.unloader.general.checks'
	_inherit = 'kmi.general.checks'

	unloader_id = fields.Many2one('kmi.unloader', string='unloader')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.unloader_id), default=True)

class KmiParamsValue(models.Model):
	_name = 'kmi.unloader.params.value'
	_inherit = 'kmi.params.value'

	unloader_id = fields.Many2one('kmi.unloader', string='Daily Report - Production Record', ondelete='cascade')
	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),
		('4', '4'),
		('5', '5'),
		('6', '6'),
		('7', '7'),
		('8', '8'),], string='Line Position')
	batch_report_id = fields.Many2one('kmi.unloader.batch.report',string='Batch Report',)
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.unloader_id), default=True)

class KmiIncompatibilityNotes(models.Model):
	_name = 'kmi.unloader.incompatibility.notes'
	_inherit = 'kmi.incompatibility.notes'

	unloader_id = fields.Many2one('kmi.unloader', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.unloader_id), default=True)