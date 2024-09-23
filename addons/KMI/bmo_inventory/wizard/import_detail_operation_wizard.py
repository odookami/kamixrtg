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
	_name = 'stock.move.line.wizard'

	file_data = fields.Binary('File')
	file_name = fields.Char('File Name')

	def raise_error(self):
		raise ValidationError(_('Harap isi tanggal Expired Date.'))
	

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
		for row_no in range(sheet.nrows):
			cont += 1
			date_year = False
			if row_no <= 0:
				fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
			else:
				line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
				date_time_obj = False
				product = product_obj.search([('default_code', '=', line[0].replace('.0',''))],limit=1)
				if not product:
					raise ValidationError(_('Item dengan internal reference {} tidak ditemukan. Harap periksa kembali master data produk tersebut.'.format(line[0])))
				if product.use_expiration_date:
					if '-' in line[4]:
						date_time_obj = datetime.strptime(line[4], '%Y-%m-%d %H:%M:%S') - timedelta(hours=7) 
					else:
						Convert_to_float = float(line[4]) if line[4] else self.raise_error()
						frmat_date = (Convert_to_float - 25569) * 86400.0
						date_time_obj = datetime.utcfromtimestamp(frmat_date)
				package = False
				if line[2]:
					package = self.env['stock.quant.package'].create({'name': line[2].replace('.0','')}).id
				location_dest_id = self.env['stock.location'].search([('name','=', line[1])], limit=1)
				if not location_dest_id:
					raise ValidationError(_("Lokasi {} tidak ditemukan. Harap periksa kembali master data lokasi tersebut.".format(line[1])))
				# print(line[1])
				picking_list_2 = [(0, 0, {
					# 'move_id'           : 
					'product_id'        : product.id,
					'product_uom_id'    : product.uom_po_id.id,
					'location_id'       : cs_obj.location_id.id,
					'location_dest_id'  : location_dest_id.id,
					'result_package_id' : package,
					'qty_done'          : line[5],
					'lot_name'          : line[3].replace('.0',''),
					'expiration_date'   : date_time_obj 
				})]
				cs_obj.write({'move_line_nosuggest_ids'    : picking_list_2})
		return True