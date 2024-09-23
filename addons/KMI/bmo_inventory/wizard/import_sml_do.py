# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.tools.translate import _
import base64
import csv
# from io import cStringIO
import io
from odoo.exceptions import Warning, ValidationError
import tempfile
import binascii
import xlrd
from datetime import date, datetime, timedelta

class ImportSml(models.TransientModel):
	_name = 'import.sml'

	file = fields.Binary('File ', required=True)
	
	def import_sml(self):
		fp = tempfile.NamedTemporaryFile(suffix=".xlsx")
		fp.write(binascii.a2b_base64(self.file))
		fp.seek(0)

		workbook = xlrd.open_workbook(fp.name)
		sheet = workbook.sheet_by_index(0)
		
		product_obj = self.env['product.product']
		picking_obj = self.env['stock.picking']
		statment_id = self._context.get('active_id')
		cs_obj = picking_obj.browse(statment_id)		
		sm = cs_obj.move_ids_without_package
		package = self.env['stock.quant.package']
		quant = self.env['stock.quant']
		
		for row_no in range(sheet.nrows):
			if row_no <= 0:
				fields = map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
			else:
				line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
				date_time_obj = False
				# print(int(float(line[0])),'==================llllllline', type(line[0]))	

				location = self.env['stock.location'].search([('name', '=', str(line[1]))], limit=1)
				location_dest_id = self.env['stock.location'].search([('name','=', 'Customers')], limit=1)
				lot = self.env['stock.production.lot'].search([('name', '=', str(line[2]))], limit=1)
				uom = self.env['uom.uom'].search([('name', '=', str(line[5].lower()))], limit=1)

				prod = product_obj.search([('id','=',lot.product_id.id)], limit=1)

				# if '-' in line[3]:
				# 	date_time_obj = datetime.strptime(line[3], '%Y-%m-%d %H:%M:%S') - timedelta(hours=7) 
				# else:
				# 	Convert_to_float = float(line[3]) if line[3] else self.raise_error()
				# 	frmat_date = (Convert_to_float - 25569) * 86400.0
				# 	date_time_obj = datetime.utcfromtimestamp(frmat_date)

				# pack_obj = package.search([('name','=', int(float(line[0])))], limit=1)
				# if not pack_obj.quant_ids:
				# 	pack = pack_obj.id
					# print(pack_obj.name,'==================pack_obj', pack)	
				print(line[1], line[2], line[0])
				quant_obj = quant.search([('product_id.default_code','=', str(line[0])),('location_id.name', '=', str(line[1])), ('lot_id.name', '=', str(line[2]))], limit=1)
				if not quant_obj:
					raise ValidationError(_("Data Tidak Ditemukan"))
				print(quant_obj)
				# for i in sm:
				vals = [(0, 0, {
					# 'move_id': cs_obj.id,
					'product_id'      : quant_obj.product_id.id,
					'location_id'	  : quant_obj.location_id.id,
					'location_dest_id': location_dest_id.id,
					'lot_id'		  : quant_obj.lot_id.id,
					'package_id': quant_obj.package_id.id,
					'product_uom_qty': line[4],
					'qty_done'		  : line[4],
					'expiration_date' : quant_obj.expiration_date,
					'product_uom_id'  : uom.id,
					'verifikator_admin'  : 'yes',
				})]
				cs_obj.write({'move_line_ids_without_package' : vals})
				reserved_quantity = uom._compute_quantity(float(line[4]), quant_obj.product_id.uom_id)
				quant_obj.write({'reserved_quantity' : reserved_quantity})
				cs_obj.immediate_transfer = True

		# 		a = cs_obj.write({'move_line_nosuggest_ids' : vals})
		# 		reserved_qty = quant_obj.reserved_quantity + float(line[4])*36
		# 		print('==========reserved_qty',reserved_qty)
		# 		print('==========a',a)

		# return a, reserved_qty

				# pack_obj.write({'location_id' : location.id})
				# quant_obj.write({'package_id' : pack})

					# i.move_line_ids.write(vals)
					# i.write({'move_line_ids'    : vals})