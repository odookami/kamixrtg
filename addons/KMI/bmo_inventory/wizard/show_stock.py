# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class StockCheckWizard(models.TransientModel):
	_name = 'wizard.dalam.wizard'

	product_id = fields.Many2one('product.product',string='Product',)