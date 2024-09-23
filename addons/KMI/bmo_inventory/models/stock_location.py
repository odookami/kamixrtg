from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class Location(models.Model):
	_inherit = "stock.location"
	
	department_id = fields.Many2one(
		'hr.department', string='Department', copy=True)
	sampling_location = fields.Boolean('Is a Sampling Location?', default=False)
	allow_quarantine = fields.Boolean(string='Allow Quarantine',)
	quarantine = fields.Boolean(string='Quarantine',)

	def name_get(self):
		res = []
		for rec in self:
			name = str(rec.complete_name)
			if rec.quarantine:
				name += " (Quarantine)"
			res.append((rec.id, name))
		return res
	
	@api.constrains('name','location_id')
	def _constrains_name_location(self):
		for o in self:
			src_location = o.search([('location_id','=',o.location_id.id),('name','=',o.name),('id','!=',o.id)])
			if src_location:
				raise UserError(_(f'{o.name} Pernah dibuat'))


class StockQuantPackage(models.Model):
	_inherit = 'stock.quant.package'
	_order = 'name asc'
	
	expiration_date = fields.Datetime(string='Expiration Date')