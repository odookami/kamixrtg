# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class QualityRejectReason(models.Model):
	_name = 'inventory.reject.reason'

	name = fields.Char(string='Reason',)

class InventoryQualityCheckTemplate(models.Model):
	_name = 'inventory.quality.check.template'
	_description = 'Inventory Quality Check Template'

	sequence = fields.Integer(string='Sequence',)
	name = fields.Char(string='Name',)

class ManufacturerPlant(models.Model):
	_name = 'manufacturer.plant'
	_description = 'Manufacturer Plant'

	name = fields.Char(string='Manufacturer Plant',)
	country_id = fields.Many2one('res.country',string='Country',)
	active = fields.Boolean(string='Archive', default=True)
	
class InventoryQualityCheck(models.Model):
	_name = 'inventory.quality.check'
	_description = ' Inventory Quality Check'

	name = fields.Char(string='Name')
	sequence = fields.Integer('Sequence')
	move_line_id = fields.Many2one('stock.move.line',string='Stock Move Line',)
	picking_id = fields.Many2one('stock.picking',string='Picking',)
	parameter = fields.Selection([('Y','Y'),('N','N'), ('-', '-')])
	parameter_text = fields.Char('Parameter(Y/N/-)', size=1)
	move_line_qc_id = fields.Many2one('stock.move.line.qc',string='Move Line QC',)

	def user_error(self):
		raise UserError(_('Parameter harus diisi oleh huruf (Y, N Atau -)'))

	@api.onchange('parameter_text')
	def _check_parameter(self):
		for rec in self:
			rec.parameter = rec.parameter_text = rec.parameter_text.upper() if rec.parameter_text in ['Y','N','y','n', '-'] else rec.user_error()
