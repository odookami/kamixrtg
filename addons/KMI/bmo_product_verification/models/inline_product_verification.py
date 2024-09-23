# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class InlineVerificationProduct(models.Model):
	_name = 'inline.product.verification'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = 'Inline Product Verification'
	_order = 'revisi desc'

	okp_id = fields.Many2one('mrp.okp',string='OKP',)
	model_id = fields.Many2one('inline.product.verification',string='Model',)
	name = fields.Char(string='Name',)
	production_date = fields.Date(string='Date', default=lambda self:fields.Date.context_today(self))
	batch_no = fields.Char(string='Batch',)
	speed_filling = fields.Float(string='Speed Filling (bpm)', default=500)
	product_id = fields.Many2one('product.product',string='Product',)
	bottle_id = fields.Many2one('bottle.type',string='Type of Bottle',)
	specific_gravity = fields.Float(string='SG (g/mL)',)
	faktor_koreksi = fields.Float(string='Faktor Koreksi', compute='_compute_faktor_koreksi')
	weight_tare = fields.Float(string='Weight Tare (g)', compute='_compute_avg_weight_tare')
	std_volume = fields.Char(string='STD Volume',)
	metode_uji = fields.Selection([
		('seal_tester', 'Seal Tester'),
		('both', 'Seal Tester & Geprek'),
		('geprek', 'Geprek'),], default='seal_tester', string='Metode Uji Kekuatan Seal')
	faktor_warna_id = fields.Many2one('faktor.warna',string='Faktor Warna',)
	pasteur_id = fields.Many2one('product.st',string='Pasteurization',)
	average = fields.Float(string='Average',)
	pic_analisa	= fields.Char(string='PIC Analisa',)
	tanggal_analisa	= fields.Date(string='Tanggal Analisa', default=lambda self:fields.Date.context_today(self))
	jam_analisa	= fields.Float(string='Jam Analisa',)
	diperiksa = fields.Char(string='Diperiksa Oleh',)
	disetujui = fields.Many2one('res.users',string='Disetujui Oleh',)
	tgl_setuju = fields.Date(string='Tgl Disetujui')
	kesimpulan = fields.Text(string='Kesimpulan',)
	note = fields.Text(string='Catatan',)
	revisi = fields.Integer('Revisi', default=0, tracking=True)
	state = fields.Selection([
		('draft', 'Draft'),
		('in_progress', 'In Progres'),
		('done','Done'),
		('draft_model', 'Draft'),
		('model', 'Model')], string='Status', default='draft', tracking=True, copy=False,)
	verification_product_line = fields.One2many('product.verification.line','verification_id',string='Verification Product Line',copy=True)
	verification_product_1_line = fields.One2many('product.verification.line','verification_id',string='Verification Product Line 1', domain=[('group','=','1')])
	verification_product_2_line = fields.One2many('product.verification.line','verification_id',string='Verification Product Line 2', domain=[('group','=','2')])
	verification_product_3_line = fields.One2many('product.verification.line','verification_id',string='Verification Product Line 3', domain=[('group','=','3')])
	analisa_verifikasi_line = fields.One2many('analisa.verifikasi','verification_id',string='Analisa 1')
	max_weight_1 = fields.Float(string='Max Weight 1', compute='_compute_max_min_avg1')
	max_weight_2 = fields.Float(string='Max Weight 2', compute='_compute_max_min_avg2')
	max_weight_3 = fields.Float(string='Max Weight 3', compute='_compute_max_min_avg3')
	min_weight_1 = fields.Float(string='Min Weight 1', compute='_compute_max_min_avg1')
	min_weight_2 = fields.Float(string='Min Weight 2', compute='_compute_max_min_avg2')
	min_weight_3 = fields.Float(string='Min Weight 3', compute='_compute_max_min_avg3')
	average_weight_1 = fields.Float(string='AVG Weight 1', compute='_compute_max_min_avg1')
	average_weight_2 = fields.Float(string='AVG Weight 2', compute='_compute_max_min_avg2')
	average_weight_3 = fields.Float(string='AVG Weight 3', compute='_compute_max_min_avg3')

	max_volume_1 = fields.Float(string='Max Volume 1', compute='_compute_max_min_avg1')
	max_volume_2 = fields.Float(string='Max Volume 2', compute='_compute_max_min_avg2')
	max_volume_3 = fields.Float(string='Max Volume 3', compute='_compute_max_min_avg3')
	min_volume_1 = fields.Float(string='Min Volume 1', compute='_compute_max_min_avg1')
	min_volume_2 = fields.Float(string='Min Volume 2', compute='_compute_max_min_avg2')
	min_volume_3 = fields.Float(string='Min Volume 3', compute='_compute_max_min_avg3')
	average_volume_1 = fields.Float(string='AVG Volume 1', compute='_compute_max_min_avg1')
	average_volume_2 = fields.Float(string='AVG Volume 2', compute='_compute_max_min_avg2')
	average_volume_3 = fields.Float(string='AVG Volume 3', compute='_compute_max_min_avg3')
	leader_check = fields.Boolean(string='Leader Check',)
	leader_need_check = fields.Boolean(string='Leader Need Check',compute='_compute_leader_need_check')
	release_date = fields.Date(string='Revision Date')

	def _compute_leader_need_check(self):
		self.leader_need_check = True if self.state == 'done' and not self.leader_check else False
		
	def action_leader_check(self):
		self.write({'leader_check' : True})

	@api.depends('verification_product_1_line')
	def _compute_max_min_avg1(self):
		for rec in self:
			rec.max_weight_1 = max(x.weight for x in rec.verification_product_1_line) if rec.verification_product_1_line else 0
			rec.min_weight_1 = min(x.weight for x in rec.verification_product_1_line) if rec.verification_product_1_line else 0
			len1 = len(rec.verification_product_1_line) if rec.verification_product_1_line else 0
			sum1 = sum(x.weight for x in rec.verification_product_1_line) if rec.verification_product_1_line else 0
			rec.average_weight_1 = sum1 / len1 if rec.verification_product_1_line else 0

			rec.max_volume_1 = max(x.volume for x in rec.verification_product_1_line) if rec.verification_product_1_line else 0
			rec.min_volume_1 = min(x.volume for x in rec.verification_product_1_line) if rec.verification_product_1_line else 0
			# len1 = len(rec.verification_product_1_line) if rec.verification_product_1_line else 0
			sum1 = sum(x.volume for x in rec.verification_product_1_line) if rec.verification_product_1_line else 0
			rec.average_volume_1 = sum1 / len1 if rec.verification_product_1_line else 0



	@api.depends('verification_product_2_line')
	def _compute_max_min_avg2(self):
		for rec in self:
			rec.max_weight_2 = max(x.weight for x in rec.verification_product_2_line) if rec.verification_product_2_line else 0
			rec.min_weight_2 = min(x.weight for x in rec.verification_product_2_line) if rec.verification_product_2_line else 0
			len2 = len(rec.verification_product_2_line) if rec.verification_product_2_line else 0
			sum2 = sum(x.weight for x in rec.verification_product_2_line) if rec.verification_product_2_line else 0
			rec.average_weight_2 = sum2 / len2 if rec.verification_product_2_line else 0

			rec.max_volume_2 = max(x.volume for x in rec.verification_product_2_line) if rec.verification_product_2_line else 0
			rec.min_volume_2 = min(x.volume for x in rec.verification_product_2_line) if rec.verification_product_2_line else 0
			# len2 = len(rec.verification_product_2_line) if rec.verification_product_2_line else 0
			sum2 = sum(x.volume for x in rec.verification_product_2_line) if rec.verification_product_2_line else 0
			rec.average_volume_2 = sum2 / len2 if rec.verification_product_2_line else 0

	@api.depends('verification_product_3_line')
	def _compute_max_min_avg3(self):
		for rec in self:
			rec.max_weight_3 = max(x.weight for x in rec.verification_product_3_line) if rec.verification_product_3_line else 0
			rec.min_weight_3 = min(x.weight for x in rec.verification_product_3_line) if rec.verification_product_3_line else 0
			len3 = len(rec.verification_product_3_line) if rec.verification_product_3_line else 0
			sum3 = sum(x.weight for x in rec.verification_product_3_line) if rec.verification_product_3_line else 0
			rec.average_weight_3 = sum3 / len3 if rec.verification_product_3_line else 0

			rec.max_volume_3 = max(x.volume for x in rec.verification_product_3_line) if rec.verification_product_3_line else 0
			rec.min_volume_3 = min(x.volume for x in rec.verification_product_3_line) if rec.verification_product_3_line else 0
			# len3 = len(rec.verification_product_3_line) if rec.verification_product_3_line else 0
			sum3 = sum(x.volume for x in rec.verification_product_3_line) if rec.verification_product_3_line else 0
			rec.average_volume_3 = sum3 / len3 if rec.verification_product_3_line else 0



	def _get_null_values(self):
		# loop batch_line
		values = self.verification_product_line.filtered(lambda l:not l.kekuatan_seal or not l.visual_check)

		return values

	def check_null_value(self):
		null_values = self._get_null_values()
		if null_values:
			raise ValidationError(_('Nozzle Nomor {} Analisa {} Belum Terisi'.format(null_values[0].number, null_values[0].group)))

	def action_approve_template(self):
		self.write({'state' : 'model', 'revisi' : self.revisi + 1})

	def action_submit(self):
		model = self.get_model()
		self.load_templates(model)
		return self.write({'state' : 'in_progress'})
		# return super(KmiDailyFilling, self).action_submit()

	def action_done(self):
		# self.check_null_value()
		if self.specific_gravity <= 0:
			raise ValidationError(_("Kolom SG tidak boleh bernilai 0"))
		return self.write({'state' : 'done', 'tgl_setuju': fields.Date.context_today(self), 'disetujui': self.env.user.id})
		# return super(KmiDailyFilling, self).action_done()

	def get_model(self):
		model = self.env['inline.product.verification'].search([('state', '=', 'model'), ('product_id', '=', self.product_id.id)],limit=1)
		return model

	def load_templates(self, model):
		if not model:
			raise ValidationError(_('Model Template Not Found, Please Check in Configuration'))
		self.write({
			'name' : model.name,
			'revisi' : model.revisi,
			'release_date' : model.release_date,
			'std_volume' : model.std_volume,
			'model_id' : model.id,
			'faktor_warna_id' : model.faktor_warna_id.id,
			'verification_product_line' : [(0,0,{'number' : x.number, 'group' : x.group, 'kekuatan_seal' :'OK', 'visual_check': 'OK'}) for x in model.verification_product_line],
			'analisa_verifikasi_line' : [(0,0,{'number' : x.number}) for x in model.analisa_verifikasi_line],
			})

	@api.onchange('pasteur_id')
	def _onchange_pasteur(self):
		self.okp_id = self.batch_no = self.product_id = False
		if self.pasteur_id:
			batch_id = self.pasteur_id.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling')
			self.write({
				'okp_id' : self.pasteur_id.okp_id.id,
				'product_id' : batch_id[0].product_id.id if batch_id else False,
				'batch_no' : self.pasteur_id.batch_id.number_ref
				})

	@api.depends('product_id', 'bottle_id')
	def _compute_faktor_koreksi(self):
		for rec in self:
			fk_obj = self.env['faktor.koreksi'].search([('product_id', '=', rec.product_id.id), ('bottle_id', '=', rec.bottle_id.id)])
			rec.faktor_koreksi = fk_obj.koreksi if fk_obj else 0
			# if rec.product_id and rec.bottle_id:

	@api.depends('analisa_verifikasi_line',)
	def _compute_avg_weight_tare(self):
		for rec in self:
			line_length = len(rec.analisa_verifikasi_line)
			sum_line = sum(x.bobot for x in rec.analisa_verifikasi_line)
			rec.weight_tare = sum_line / line_length if rec.analisa_verifikasi_line else 0


class AnalisaVerifikasi(models.Model):
	_name = 'analisa.verifikasi'
	_description = 'Analisa Verifikasi'

	verification_id = fields.Many2one('inline.product.verification',string='Product Verification',)
	number = fields.Integer(string='No.',)
	bobot = fields.Float(string='Bobot (gr)',)


class VerificationProductLine(models.Model):
	_name = 'product.verification.line'
	_description = 'Product Verification Line'

	verification_id = fields.Many2one('inline.product.verification',string='Verification ID',)
	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),], string='Group Table')
	number = fields.Integer(string='Number of Nozzle',)
	weight = fields.Float(string='Weight(g)',)
	volume = fields.Float(string='Volume (ml)', compute='_compute_volume', store=True,)
	color = fields.Selection([
		('primary', 'Primary'),
		('danger', 'Danger'),
		('warning', 'Warning'),
		], string='Color', compute='_compute_warna')
	# kekuatan_seal = fields.Selection([
	# 	('OK', 'OK'),
	# 	('bad_seal', 'Bad Seal'),
	# 	('unseal', 'Unseal')], string='Kekuatan Seal')
	# visual_check = fields.Selection([
	# 	('OK', 'OK'),
	# 	('not_ok', 'Not OK'),], string='Visual Check')
	kekuatan_seal = fields.Char(string='Kekuatan Seal',)
	visual_check = fields.Char(string='Visual Check',)
	editable = fields.Boolean(string='Is Editable',compute=lambda self:self._user_can_edit(self.verification_id), default=True)

	def _user_can_edit(self, parent_id):
		for line in self:
			if self.user_has_groups('bmo_batch_record.group_batch_record_edit') and parent_id.state == 'done':
				line.editable = True
			elif parent_id.state == 'in_progress':
				line.editable = True
			else:
				line.editable = False

	@api.depends('verification_id.faktor_warna_id', 'volume')
	def _compute_warna(self):
		for rec in self:
			target = rec.verification_id.faktor_warna_id.target.split('-') if rec.verification_id.faktor_warna_id else [1,2]
			# out_range = rec.verification_id.faktor_warna_id.out_range.split('-') if rec.verification_id.faktor_warna_id else [1,2]
			if rec.volume <=  float(rec.verification_id.faktor_warna_id.yellow) or rec.volume >= float(rec.verification_id.faktor_warna_id.blue):
				# print('MASUK MERAH')
				rec.color = 'danger' if rec.volume != 0 else False
			elif rec.volume < float(target[0]) and rec.volume > float(rec.verification_id.faktor_warna_id.yellow):
				# print('MASUK KUNING')
				rec.color = 'warning'
			elif rec.volume >= float(target[1]) and rec.volume < float(rec.verification_id.faktor_warna_id.blue):
				# print('MASUK BIRU')
				rec.color = 'primary'
			else:
				# print('ELSEEE')
				rec.color = False


	@api.depends('verification_id.weight_tare', 'verification_id.faktor_koreksi', 'verification_id.specific_gravity', 'weight')
	def _compute_volume(self):
		for rec in self:
			volume_1 = ((rec.weight - rec.verification_id.weight_tare) / rec.verification_id.specific_gravity) if rec.verification_id.specific_gravity else 0
			rec.volume = volume_1 + rec.verification_id.faktor_koreksi if rec.weight > 0 else 0
		# ((berat – weight tare)/sg ml)+koreksi