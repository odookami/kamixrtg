# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class Picking(models.Model):
	_inherit = 'stock.picking'

	dumping_created = fields.Boolean(string='Dumping Created',default=False, copy=False)
	need_dumping_create = fields.Boolean(string='Need Dumping Create', compute='_need_dumping_create')

	@api.depends('state', 'generate_okp')
	def _need_dumping_create(self):
		for picking in self:
			picking.need_dumping_create = False
			if picking.state == 'done' and picking.generate_okp and not picking.dumping_created:
				picking.need_dumping_create = True

	def create_dumping(self):
		dumping_obj = self.env['kmi.dumping'].create({
			'okp_id' : self.batch_production_id.okp_id.id,
			'mo_id' : self.mo_id.id,
			'product_id' : self.mo_id.product_id.id,
			'date' : fields.Date.context_today(self),
			# 'shift' : self.mo_id.shift,
			'name' : 'New'
			})

		self.dumping_created = True
		self.message_post(
                    body=_('Batch Record Dumping <a href=# data-oe-model=kmi.dumping data-oe-id={id} date-oe-action={action}>{display_name}</a> has been created.'.format(id=dumping_obj.id, action=self.env.ref('bmo_dumping.action_kmi_dumping').id, display_name=dumping_obj.display_name)))