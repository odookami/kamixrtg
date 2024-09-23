# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class ProductTemplate(models.Model):
	_inherit = 'product.template'

	invoice_uom_id = fields.Many2one('uom.uom',string='Invoice UoM',)