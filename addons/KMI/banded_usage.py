import json
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class BandedUsage(models.Model):
	_name = 'banded.usage'
	_inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
	_description = 'Stock Card Banded'

	name = fields.Char('Name', default='FRM-PRD-095', tracking=True, copy=False)
	date = fields.Date("Date", track_visibility='always')
	shift = fields.Selection([
		('I', 'I'), ('II', 'II'),
		('III', 'III')], string='Shift', tracking=True)
	team = fields.Selection([('A', 'A'), ('B', 'B'),
		('C', 'C')], 'Team', default='A', tracking=True)
	location_id = fields.Many2one('stock.location', string="Location")
	state = fields.Selection([
		('draft', 'Draft'), 
		('in_progress', 'In Progress'),
		('done', 'Done'), 
		('cancel', 'Cancel')], 'Status', default='draft', tracking=True, copy=False)
	note_line_1 = fields.Text('Note', tracking=True)
	note_line_2 = fields.Text('Note', tracking=True)
	
	material_usage_ids = fields.One2many('banded.usage.line', 
		'banded_usage_id', string='Material Line Usage')
	material_usage_1_ids = fields.One2many('banded.usage.line', 
		'banded_usage_1_id', string='Material Line 1 Usage')
	material_usage_2_ids = fields.One2many('banded.usage.line', 
		'banded_usage_2_id', string='Material Line 2 Usage')

	material_usage_line_1 = fields.One2many('banded.usage.line', 
		'banded_usage_id', string='Material Usage', domain=[('group','=','1')])
	material_usage_line_2 = fields.One2many('banded.usage.line', 
		'banded_usage_id', string='Material Usage', domain=[('group','=','2')])

	leader_check = fields.Boolean(string='Leader Check',)
	leader_need_check = fields.Boolean(string='Leader Need Check',compute='_compute_leader_need_check')

	editable = fields.Boolean(string='Editable', compute='_user_can_edit', default=True)

	def _user_can_edit(self):
		for rec in self:
			if self.user_has_groups('bmo_mrp.group_mrp_leader'):
				rec.editable = True
			else:
				rec.editable = False
	
	@api.onchange('date')
	def _onchange_loc(self):
		if self.date:
			# id prod/staging
			self.location_id = 5268
	
	def action_leader_check(self):
		self.write({'leader_check' : True})

	def action_submit(self):
		return self.write({'state' : 'in_progress'})

	def action_done(self):
		for o in self:
			o.write({'state' : 'done'})

	def _compute_leader_need_check(self):
		self.leader_need_check = True if self.state == 'done' and not self.leader_check else False
		
	def action_leader_check(self):
		self.write({'leader_check' : True})
	
	def action_cancel(self):
		for o in self:
			o.write({'state' : 'cancel'})

class BandedUsageLine(models.Model):
	_name = 'banded.usage.line'

	banded_usage_id = fields.Many2one('banded.usage', ondelete='cascade')
	banded_usage_1_id = fields.Many2one('banded.usage', ondelete='cascade')
	banded_usage_2_id = fields.Many2one('banded.usage', ondelete='cascade')
	item_id = fields.Many2one('product.product',string='Item Code')
	item_name = fields.Char(string='Prod Name', related='item_id.name')
	# material_banded_6 = fields.Char(string='Banded 6')
	# material_single = fields.Char(string='Single')
	product_banded_id = fields.Many2one('product.product',string='Banded 6')
	product_single_id = fields.Many2one('product.product',string='Single ')
	product_varian_id = fields.Many2one('product.product',string='Varian Product ')

	lot_id = fields.Many2one('stock.production.lot',string='Lot')
	lot_domain = fields.Char(string='Lot Domain', compute='_compute_lot_domain')
	uom_id = fields.Many2one('uom.uom',string='Satuan', related='item_id.uom_id')
	first_stock = fields.Float(string='First Stock')
	out = fields.Float(string='Out')
	reject = fields.Float(string='Reject')
	total_out = fields.Float(string='Total Out', compute='_compute_total')
	last_stock = fields.Float(string='Last Stock', compute='_compute_total')

	jam_roll = fields.Float('Jam Ganti Roll')
	start = fields.Float('Start')
	finish = fields.Float('Finish')
	total_waktu = fields.Float('Total Waktu', compute='_compute_total_hour') 

	editable = fields.Boolean(string='Editable', compute='_user_can_edit', default=True)

	def _user_can_edit(self):
		for rec in self:
			if self.user_has_groups('bmo_mrp.group_mrp_leader'):
				rec.editable = True
			else:
				rec.editable = False
	
	group = fields.Selection([
		('1', '1'),
		('2', '2'),
		('3', '3'),], string='Line Position')
	
	@api.depends('item_id', 'banded_usage_id.location_id')
	def _compute_lot_domain(self):
		for rec in self:
			rec.lot_domain = json.dumps([('id', '=', 0)])
			# rec.lot_id = False
			quant = self.env['stock.quant']
			lot_ids = []
			if rec.item_id and rec.banded_usage_id.location_id:
				lot_ids = quant.search([('product_id', '=', rec.item_id.id), 
					('location_id','=', rec.banded_usage_id.location_id.id)]).mapped('lot_id').ids
				# print(lot_ids)
				rec.lot_domain = json.dumps(
					[('id', 'in', lot_ids)]
				)
	
	@api.depends('out','reject','first_stock')
	def _compute_total(self):
		for s in self:
			s.total_out = s.out + s.reject
			s.last_stock = s.first_stock - (s.out + s.reject)
	
	@api.onchange('lot_id')
	def _onchange_lot(self):
		for s in self:
			quant = self.env['stock.quant']
			src = quant.search([('location_id','=',s.banded_usage_id.location_id.id),('product_id','=', s.item_id.id),('lot_id','=',s.lot_id.id)])
			if s.lot_id:
				s.first_stock = src.quantity if src else 0
	
	@api.depends('start', 'finish')
	def _compute_total_hour(self):
		for record in self:
			result = record.finish - record.start
			record.total_waktu = result if record.total_waktu <= 0 else 0