# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from lxml import etree
import simplejson as json
from datetime import date


class StockMoveLine(models.Model):
	_inherit = 'stock.move.line'


	quality_check_line = fields.One2many('inventory.quality.check','move_line_id',string='Quality Check Line',)
	# sml_qc_line = fields.One2many('stock.move.line.qc','sml_id',string='Stock Move Line QC',)

	@api.model
	def fields_view_get(self, view_id=None, view_type='tree', toolbar=False, submenu=False):
		result = super(StockMoveLine, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
		doc = etree.XML(result['arch'])
		if view_type == 'tree' and self.user_has_groups('bmo_inventory_qc.group_warehouse'):
			doc.set('editable','bottom')
			result['arch'] = etree.tostring(doc)
		return result



	def create_qc(self, qc_values):
		sml_qc_line_values = dict()

		for line in self:
			sml_ids = []
			# print(line.lot_name)
			if line.lot_id.id not in sml_qc_line_values:
				sml_qc_line_values[line.lot_id.id] = {
					'product_id' : line.product_id.id,
					# 'location_dest_id' : line.location_dest_id.id,
					'qty' : line.qty_done,
					'lot_id' : line.lot_id.id if line.lot_id else False,
					'uom_id' : line.product_uom_id.id,
					'stock_move_id' : line.move_id.id,
					'quality_check_line' : qc_values,
				}
			else:
				sml_qc_line_values[line.lot_id.id]['qty'] += line.qty_done
		return sml_qc_line_values