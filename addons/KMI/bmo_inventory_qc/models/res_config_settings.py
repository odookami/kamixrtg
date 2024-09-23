# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class Company(models.Model):
	_inherit = 'res.company'

	receipt_allowance = fields.Float(string='Receipt Allowance',)



class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'

	receipt_allowance = fields.Float(string='Receipt Allowance',related='company_id.receipt_allowance', readonly=False,)
