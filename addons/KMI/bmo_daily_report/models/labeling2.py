# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class KmiLabeling2(models.Model):
	_name = 'kmi.labeling2'
	_inherit = 'kmi.daily.report'

	active = fields.Boolean('Active', default='True')
	model_id = fields.Many2one('kmi.retort',string='Model',)

	conversion_line = fields.One2many('kmi.labeling2.params.value', 
		'labeling2_daily_report_id', string='Roll to Kg Reject Qty Conversion')
	material_line = fields.One2many('kmi.labeling2.material.usage', 
		'labeling2_daily_report_id', string='Material Usage')
	incompatibility_line = fields.One2many('kmi.labeling2.incompatibility.notes', 
		'labeling2_id', string='Catatan Proses Produksi')


	material_usage_note = fields.Text(string='Notes',)
	labeling2_note = fields.Text(string='Another Awesome Notes', copy=False,
		default="""	 * Condition OK means : clean, no straching sound, in a good shape
		* Machine stop under 30 min ditulis pada minor breakdown (Form Efficiency)
		* SPV melakukan tanda tangan bila mereview form
		* Bila belt leak check kotor, segera dibersihkan dengan brush dan air per 2 jam
		* Reject SLA yang dibuang pada saat produksi """)

	def get_model(self):
		model = self.env['kmi.labeling2'].search([('state', '=', 'model')],limit=1)
		return model
	
	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		return super(KmiLabeling2, self).action_submit()
	
	def action_done(self):
		self.check_null_value()
		return super(KmiLabeling2, self).action_done()

class KmiParamsValue(models.Model):
	_name = 'kmi.labeling2.params.value'
	_inherit = 'kmi.params.value'

	labeling2_daily_report_id = fields.Many2one('kmi.labeling2', 
		string='Daily Report - Labeling 2', ondelete='cascade')
	product_type = fields.Selection(string='Product', 
		selection=[('Produk CGM/HI C', 'Produk CGM/HI C'), 
		('Produk NBE/Fishot', 'Produk NBE/Fishot'),])
	reject_pcs = fields.Float(string='Reject pcs', 
		compute='_compute_rpcs', readonly=False)
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
	
	# @api.depends('product_type')
	# def _compute_rpcs(self):
	# 	for record in self:
	# 		result = 0
	# 		label_line = record.labeling2_daily_report_id.label_line
	# 		result = sum((x.ss_join + x.ss_actual + x.kmi_slice) \
	# 			for x in label_line) if label_line and record.product_type else 0
	# 		record.reject_pcs = result if record.reject_pcs <= 0 else 0

	# @api.depends('reject_pcs')
	# def _compute_rpcs_m(self):
	# 	for record in self:
	# 		result = (record.reject_pcs * 10.3) / 100 if record.reject_pcs else 0
	# 		record.reject_pcs_m = result if record.reject_pcs_m <= 0 else 0
	
	# @api.depends('reject_cm')
	# def _compute_cm_m(self):
	# 	for record in self:
	# 		result = (record.reject_cm / 100) if record.reject_cm else 0
	# 		record.reject_cm_m = result if record.reject_cm_m <= 0 else 0

	# @api.depends('reject_pcs_m', 'std_pcs')
	# def _compute_rrpcs(self):
	# 	for record in self:
	# 		result = (record.reject_pcs_m / record.std_pcs) \
	# 			if record.reject_pcs_m and record.std_pcs else 0
	# 		record.reject_rpcs = result if record.reject_rpcs <= 0 else 0
	
	# @api.depends('reject_cm_m', 'std_cm')
	# def _compute_rrcm(self):
	# 	for record in self:
	# 		result = (record.reject_cm_m / record.std_cm) \
	# 			if record.reject_cm_m and record.std_cm else 0
	# 		record.reject_rcm = result if record.reject_rcm <= 0 else 0

	# @api.depends('reject_rpcs', 'reject_rcm')
	# def _compute_total(self):
	# 	for record in self:
	# 		result = record.reject_rpcs + record.reject_rcm
	# 		record.total_reject = result if record.total_reject <= 0 else 0

class Kmilabeling2MaterialUsage(models.Model):
	_name = 'kmi.labeling2.material.usage'
	_inherit = 'kmi.material.usage'

	first_stock = fields.Float('First stock (Netto)')
	in_minute = fields.Float('In minutes')
	reject = fields.Float('Reject')
	note = fields.Text('Notes')
	lot_id = fields.Many2one('stock.production.lot',string='Lot',)

	labeling2_daily_report_id = fields.Many2one('kmi.labeling2', 
		string='Laporan Harian', ondelete='cascade')
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.filling_daily_report_id), default=True)

class KmiIncompatibilityNotes(models.Model):
	_name = 'kmi.labeling2.incompatibility.notes'
	_inherit = 'kmi.incompatibility.notes'

	labeling2_id = fields.Many2one('kmi.labeling2', 
		string='Laporan Harian', ondelete='cascade')