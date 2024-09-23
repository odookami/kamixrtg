# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class MrpProductonPackingLine(models.Model):
	_inherit = 'mrp.production.packing.line'

	checked = fields.Boolean(string='QC Checked', help="Menandakan line ini sudah masuk ke dalam QC Release Finish Good,")


	def action_release(self):
		res = super(MrpProductonPackingLine, self).action_release()
		for rec in self:
			rec.location_dest_id.write({"quarantine" : True if rec.packing_type == 'Banded' else False})
		return res