# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class GetPartner(models.TransientModel):
	_name = 'get.partner.wizard'
	_description = 'Get Partner Wizard'

	partners = fields.Many2many('res.partner',string='Partners',)

	@api.model
	def default_get(self, fields):
		res = super(GetPartner, self).default_get(fields)
		partner = self.env['res.partner'].search([('cust_acct_site_id', '!=', 0)])
		if partner:
			res.update({
				'partners' : [(6,0,partner.ids)]
				})
		print(partner.mapped('cust_acct_site_id'))
		return res


	def get_customer(self):
		partner_obj = self.env['res.partner']
		partners = partner_obj.grab_supplier(where_condition=self.partners.mapped('cust_acct_site_id'))
		action = self.env.ref('contacts.action_contacts').read()[0]
		action['domain'] = [('id', 'in', partners.ids)]
		action['view_mode'] = 'tree'
		return action
		# print(partners)