# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class ProductSt(models.Model):
	_inherit = 'product.st'

	def move_to_product_verification(self):
		verification_id = self.env['inline.product.verification']
		okp_verification_id = self.okp_id.batch_mo_line.filtered(lambda l:l.tipe == 'Filling')
		# if verification_id:
			# verification_id.write({'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_verification_id[0].product_id.id})]})
		verification_id = verification_id.create({
			'name' : 'New',
			'okp_id' : self.okp_id.id,
			'production_date' : fields.Date.context_today(self),
			'product_id' : okp_verification_id[0].product_id.id,
			'batch_no' : self.batch_id.number_ref,
			'pasteur_id' : self.id,
			# 'batch_line' : [(0,0,{'batch_number' : self.batch_id.number_ref, 'product_id' : okp_verification_id[0].product_id.id})],
			})


	def action_done(self):
		super(ProductSt, self).action_done()
		self.move_to_product_verification()