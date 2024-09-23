# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class KmiDumping(models.Model):
	_inherit = 'kmi.dumping'

	def action_release(self):
		super(KmiDumping, self).action_release()
		self.create_pasteurisasi()

	def create_pasteurisasi(self):
		pasteur_obj = self.env['product.st'].create({
			'okp_id' : self.okp_id.id,
			'batch_id' : self.mo_id.id,
			'product_id' : self.product_id.id,
			'date' : fields.Date.context_today(self),
			# 'shift' : self.mo_id.shift,
			'name' : 'New'
			})

		# self.dumping_created = True
		self.message_post(
                    body=_('Batch Record Dumping <a href=# data-oe-model=product.st data-oe-id={id} date-oe-action={action}>{display_name}</a> has been created.'.format(id=pasteur_obj.id, action=self.env.ref('bmo_dumping.action_kmi_dumping').id, display_name=pasteur_obj.display_name)))