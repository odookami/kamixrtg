from odoo import api, exceptions, fields, models, _
import tempfile
import binascii
import itertools
import xlrd
import base64
import io
from odoo.tools import pycompat
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta


class Picking_wizard(models.TransientModel):
	_name = 'picking.wizard'

	file_data = fields.Binary('File')
	file_name = fields.Char('File Name')
	

	def import_picking(self):
		if not self.file_name:
			raise ValidationError(_('Unselected file'))
		
		fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
		fp.write(binascii.a2b_base64(self.file_data))
		fp.seek(0)

		workbook = xlrd.open_workbook(fp.name)
		sheet = workbook.sheet_by_index(0)
		
		product_obj = self.env['product.product']
		picking_list_2 = []
		
		obj_import = self.env["stock.picking"]
		picking_id = self.env.context.get('active_id')
		cs_obj = obj_import.browse(picking_id)
		
		
		cont = 0
		lines = []
		for row_no in range(sheet.nrows):
			cont += 1
			date_year = False
			if row_no <= 0:
				fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
			else:
				line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
				
				if line[3]:
					partner = self.env['res.partner'].search([('name','ilike',line[3])], limit=1).id
				else:
					partner = cs_obj.partner_id.id

				if line[1]:
					if line[0] and line[1]:
						raise ValidationError(_('Kolom Product dan Product Group tidak boleh berada pada baris yang sama.'))
					print(line[1])
					group_obj = self.env['product.group'].search([('code', '=', line[1])])
					print(group_obj)
					if not group_obj:
						raise ValidationError(_('Product Group Tidak Ditemukan.'))
					lines = [(0,0,{
						'name'              : pgl.product_id.name,
						'picking_id'        : picking_id,
						'product_id'        : pgl.product_id.id,
						'vendor_id'         : partner or False,
						'product_uom_qty'   : pgl.qty * float(line[2]),
						'product_uom'       : pgl.uom_id.id,
						'picking_type_id'   : cs_obj.picking_type_id.id,
						'location_id'       : cs_obj.location_id.id,
						'location_dest_id'  : cs_obj.location_dest_id.id,
					}) for pgl in group_obj.product_group_line]
					cs_obj.write({'move_ids_without_package'    : lines})
				else:
					product = product_obj.search([('default_code', '=', line[0])],limit=1)
					if not product:
						raise ValidationError(_('Item dengan internal reference {} tidak ditemukan. Harap periksa kembali master data produk tersebut.'.format(line[0])))
				# print(product)
					lines = [(0,0,{
						'name'              : product.name,
						'picking_id'        : picking_id,
						'product_id'        : product.id,
						'vendor_id'         : partner or False,
						'product_uom_qty'   : line[2],
						'product_uom'       : product.uom_po_id.id,
						'picking_type_id'   : cs_obj.picking_type_id.id,
						'location_id'       : cs_obj.location_id.id,
						'location_dest_id'  : cs_obj.location_dest_id.id,
					})]
					cs_obj.write({'move_ids_without_package'    : lines})
		cs_obj.action_confirm()
		return True
	

class PopDemanWizard(models.TransientModel):
	_name = 'pop.deman.wizard'

	note = fields.Text('Note', readonly=True)
	picking_id = fields.Many2one('stock.picking', 'Picking')

	def action_deman(self):
		for rec in self:
			rec.picking_id.is_open_popup = True
			rec.picking_id.sudo().button_validate()