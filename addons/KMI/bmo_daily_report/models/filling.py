# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import json
from odoo.exceptions import ValidationError

class KmiDailyFilling(models.Model):
	_name = 'kmi.filling'
	_inherit = 'kmi.daily.report'
	_description = 'KMI Filling Maching'
	_order = 'revision desc'

	active = fields.Boolean('Active', default='True')
	cip = fields.Float(string='CIP')
	total_output_shift = fields.Float('Total output / shift')
	total_output_hours = fields.Float('Total output / running hours')
	filling_note = fields.Text(string='Another Awesome Notes', copy=False,
		default=""" * Condition OK means : clean, no straching sound, in a good shape
			* Jam Start : mengacu jam produk yang pertama kali keluar filling
			* Jam Finish : mengacu jam produk yang terakhir kali keluar filling """)
	product_id = fields.Many2one('product.product',string='Product',)
	product_filling_id = fields.Many2one('product.product',string='Allufoil',)
	location_id = fields.Many2one('stock.location', string='Location')

	run_production = fields.Char('Running Production')
	cip = fields.Char('CIP (what step)')
	prep_filling = fields.Char('Preparation')
	other = fields.Char('Other')

	# One2many
	batch_line = fields.One2many('kmi.filling.batch.report', 'filling_batch_line_id', string='Batch Line')
	checks_line = fields.One2many('kmi.filling.general.check', 'filling_check_id', string='General Checks', domain=[('group','!=', '2')])
	checks_2_line = fields.One2many('kmi.filling.general.check', 'filling_check_id', string='General Checks 2', domain=[('group','=', '2')])
	verify_coding_line = fields.One2many('kmi.filling.verify.coding', 'filling_report_id', string='Verifikasi Coding')
	filling_params_line = fields.One2many('kmi.filling.params','filling_id', string='Filling Params',)
	parameter_mesin_1_line = fields.One2many('kmi.filling.params', 'filling_params_id', string='Parameter Mesin')
	parameter_mesin_2_line = fields.One2many('kmi.filling.params', 'filling_params_2_id', string='Parameter Mesin 2')
	params_seal_line = fields.One2many('kmi.filling.params', 'filling_param_seal_id', string='Parameter Production')
	cip_line = fields.One2many('kmi.cip.line','filling_id',string='Cleaning in Place',)
	filling_cip_line = fields.One2many('kmi.cip.line','filling_cip_id',string='Filling CIP',)
	after_cip_line = fields.One2many('kmi.cip.line','filling_after_cip_id',string='After CIP',)
	step_cip_line = fields.One2many('step.cip.line','filling_id',string='Step CIP 1',)
	pre_rinse_line = fields.One2many('step.cip.line','filling_id',string='Step CIP 1',)
	caustic_lye_line = fields.One2many('step.cip.line','filling_id',string='Step CIP 1',)
	intermediete_rinse_line = fields.One2many('step.cip.line','filling_id',string='Step CIP 1',)
	acid_line = fields.One2many('step.cip.line','filling_id',string='Step CIP 1',)
	final_rinse_line = fields.One2many('step.cip.line','filling_id',string='Step CIP 1',)
	hot_water_line = fields.One2many('step.cip.line','filling_id',string='Step CIP 1',)
	material_line = fields.One2many('kmi.filling.material.usage', 'filling_daily_report_id', string='Material Usage')
	incompatibility_line = fields.One2many('kmi.filling.incompatibility.notes', 'filling_daily_report_id', string='Catatan Proses Produksi')
	total_reject_produk = fields.Float(string='Total Reject Produk', compute='_compute_total_reject')

	# Notes
	material_usage_note = fields.Text(string='Notes',)
	note_vefiri_coding = fields.Text('Verifikasi Coding Box')

	@api.depends('batch_line')
	def _compute_total_reject(self):
		self.total_reject_produk = sum(x.reject_batch for x in self.batch_line)

	def name_get(self):
		res = []
		for rec in self:
			name = "[{}] {}".format(str(rec.no_urut_bo), str(rec.name)) if rec.no_urut_bo else str(rec.name)
			res.append((rec.id, name))
		return res

	def _get_null_values(self):
		# loop batch_line
		# values = []
		values = [x.set_coding_by_qc for x in self.verify_coding_line.filtered(lambda l:not all([l.set_coding_by_qc, l.actual_coding, l.pic_produksi, l.jam_cetak_coding, l.pic_qc, l.jam_verifikasi_coding, l.status_verifikasi]))]
			# + [x.name for x in self.checks_line.filtered(lambda l: not l.matching)] \
			# + [x.set_coding_by_qc for x in self.verify_coding_line.filtered(lambda l:not all([l.set_coding_by_qc, l.actual_coding, l.pic_produksi, l.jam_cetak_coding, l.pic_qc, l.jam_verifikasi_coding, l.status_verifikasi]))] \
			# + [x.name for x in self.parameter_mesin_1_line.filtered(lambda l: not all([l.param_1, l.param_2, l.param_3, l.param_4, l.param_5, l.param_6, l.param_7, l.param_8]))]\
			# + [x.name for x in self.parameter_mesin_2_line.filtered(lambda l: not all([l.check_time1, l.check_time2]))]\
			# + [x.name for x in self.params_seal_line.filtered(lambda l: not any([l.param_1, l.param_2, l.param_3, l.param_4, l.param_5, l.param_6, l.param_7, l.param_8]))]\
			# + [x.name for x in self.cip_line.filtered(lambda l: not l.matching)]

		return values

	def check_null_value(self):
		null_values = self._get_null_values()
		if null_values:
			raise ValidationError(_('{} Belum Terisi Atau Belum Sesuai STD'.format(null_values[0])))

	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		return super(KmiDailyFilling, self).action_submit()

	def action_done(self):
		# self.check_null_value()
		return super(KmiDailyFilling, self).action_done()

	def get_model(self):
		model = self.env['kmi.filling'].search([('state', '=', 'model')],limit=1)
		return model

	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))
		print(list(x.no for x in model.step_cip_line))
		self.write({
			'name' : model.name,
			'revision' : model.revision,
			'release_date' : model.release_date,
			'location_id' : model.location_id.id,
			'checks_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'group' : x.group}) for x in model.checks_line],
			'checks_2_line' : [(0,0,{'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'group' : x.group}) for x in model.checks_2_line],
			'parameter_mesin_1_line' : [(0,0,{'name' : x.name, 'filling_id' : self.id}) for x in model.parameter_mesin_1_line],
			'parameter_mesin_2_line' : [(0,0,{'name' : x.name, 'filling_id' : self.id}) for x in model.parameter_mesin_2_line],
			'params_seal_line' : [(0,0,{'name' : x.name, 'filling_id' : self.id}) for x in model.params_seal_line],
			'filling_cip_line' : [(0,0,{'no' : x.no, 'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'filling_id' : self.id}) for x in model.filling_cip_line],
			'after_cip_line' : [(0,0,{'no' : x.no, 'name' : x.name, 'standard' : x.standard, 'type_operation' : x.type_operation, 'filling_id' : self.id}) for x in model.after_cip_line],
			'step_cip_line' : [(0,0,{'no': x.no}) for x in model.step_cip_line],
			})


class KmiFillingStepCip(models.Model):
	_name = 'step.cip.line'
	_description = 'Step CIP'

	filling_id = fields.Many2one('kmi.filling',string='Filling',)
	no = fields.Char('Nomor')
	pre_rinse_start = fields.Float('Start')
	pre_rinse_stop = fields.Float('Stop')
	caustic_lye_start = fields.Float('Start')
	caustic_lye_stop = fields.Float('Stop')
	inter_rinse_start = fields.Float('Start')
	inter_rinse_stop = fields.Float('Stop')
	acid_start = fields.Float('Start')
	acid_stop = fields.Float('Stop')
	final_rinse_start = fields.Float('Start')
	final_rinse_stop = fields.Float('Stop')
	final_rinse_ph = fields.Float('Ph')
	hot_water_start = fields.Float('Start')
	hot_water_stop = fields.Float('Stop')
	hot_water_ph = fields.Float('Ph')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_id), default=True)

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state in ('draft','in_progress'):
				line.editable = True
			else:
				line.editable = False

class KmiFillingBatchReport(models.Model):
	_name = 'kmi.filling.batch.report'
	_inherit = 'kmi.batch.report'

	filling_batch_line_id = fields.Many2one('kmi.filling', 
		string='Batch Report Line', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_batch_line_id), default=True)
	
class KmiFillingVerifyCoding(models.Model):
	_name = 'kmi.filling.verify.coding'
	_inherit = 'kmi.verify.coding'
	_description = 'VERIFIKASI CODING BODI'

	filling_report_id = fields.Many2one('kmi.filling', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_report_id), default=True)
	

class KmiGeneralCheck(models.Model):
	_name = 'kmi.filling.general.check'
	_inherit = 'kmi.general.checks'
	_description = 'Filling General Check'

	filling_check_id = fields.Many2one('kmi.filling', string='Filling')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_check_id), default=True)
	group = fields.Selection([
		('1', '1'),
		('2', '2')], string='Line Position')

	# @api.onchange('actual')
	# def onchange_actual(self):
	# 	for line in self:
	# 		line.check_standard_value()

class KmiCipFilling(models.Model):
	_name = 'kmi.cip.line'
	_inherit = 'kmi.general.checks'
	_description = 'KMI Cleaning in Place'

	filling_id = fields.Many2one('kmi.filling',string='Filling',)
	filling_cip_id = fields.Many2one('kmi.filling',string='Filling CIP',)
	filling_after_cip_id = fields.Many2one('kmi.filling',string='Filling After CIP',)
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_id), default=True)

	# @api.onchange('actual')
	# def onchange_actual(self):
	# 	for line in self:
	# 		line.check_standard_value()


class KmiFillingParamsValue(models.Model):
	_name = 'kmi.filling.params'
	_inherit = 'kmi.params.value'
	_description = 'Parameter Value'

	filling_id = fields.Many2one('kmi.filling',string='Filling')
	filling_params_id = fields.Many2one('kmi.filling', string='Parameter Mesin', ondelete='cascade')
	filling_params_2_id = fields.Many2one('kmi.filling', string='Parameter Mesin 2', ondelete='cascade')
	filling_report_mch_id = fields.Many2one('kmi.filling', string='MCH Sealer Machine', ondelete='cascade')
	filling_param_seal_id = fields.Many2one('kmi.filling', string='Sealer Machine', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_id), default=True)
	
class KmiFillingMaterialUsage(models.Model):
	_name = 'kmi.filling.material.usage'
	_inherit = 'kmi.material.usage'

	first_stock = fields.Float('First stock (Netto)')
	in_minute = fields.Float('In minutes', compute='_compute_in_minutes')
	reject = fields.Float('Reject')
	note = fields.Text('Notes')
	lot_id = fields.Many2one('stock.production.lot',string='Lot',)

	filling_daily_report_id = fields.Many2one('kmi.filling', 
		string='Laporan Harian', ondelete='cascade')
	# last_stock = fields.Float(string='Last stock', compute='_compute_last_stock')

	lot_domain = fields.Char(string='Lot Domain', compute='_compute_lot_domain')#domain=lambda self:self._onchange_domain_lot())
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_daily_report_id), default=True)
	last_stock = fields.Float(string='Last stock', compute='_compute_last_stock')

	@api.depends('start', 'finish')
	def _compute_in_minutes(self):
		for rec in self:
			in_hour = rec.finish - rec.start
			rec.in_minute = in_hour * 60

	@api.depends('first_stock', 'out_qty', 'reject')
	def _compute_last_stock(self):
		# self.ensure_one()
		for rec in self:
			comp_1 = rec.out_qty + rec.reject
			rec.last_stock = rec.first_stock - comp_1

	@api.onchange('filling_daily_report_id.product_filling_id')	
	def _onchange_domain_lot(self):
		self.ensure_one()

		domain = [('id','=',False)]
		print('asdfasdfsdf')

	@api.depends('filling_daily_report_id.product_filling_id', 'filling_daily_report_id.location_id')
	def _compute_lot_domain(self):
		for rec in self:
			# print('asdfsdfgsdfgdfgkjhldkjhl')
			rec.lot_domain = json.dumps([('id', '=', 0)])
			# rec.lot_id = False
			quant = self.env['stock.quant']
			lot_ids = []
			if rec.filling_daily_report_id.product_filling_id and rec.filling_daily_report_id.location_id:
			# koment untuk sementara
				lot_ids = quant.search([('product_id', '=', rec.filling_daily_report_id.product_filling_id.id), 
					('location_id','=', rec.filling_daily_report_id.location_id.id)]).mapped('lot_id').ids
				print(lot_ids)
				rec.lot_domain = json.dumps(
					[('id', 'in', lot_ids)]
				)
			# yg dibawah ini biar kebuka semua
			# 	lot_ids = self.env['stock.production.lot'].search([('product_id', '=', rec.filling_daily_report_id.product_filling_id.id)]).ids
			# 	rec.lot_domain = json.dumps(
			# 		[('id', 'in', lot_ids)]
			# 	)



class KmiFillingIncompatibilityNotes(models.Model):
	_name = 'kmi.filling.incompatibility.notes'
	_inherit = 'kmi.incompatibility.notes'

	filling_daily_report_id = fields.Many2one('kmi.filling', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_daily_report_id), default=True)
