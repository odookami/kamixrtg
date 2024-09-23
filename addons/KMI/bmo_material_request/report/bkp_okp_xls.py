# -*- coding: utf-8 -*-

import io
import os
import base64
from dateutil import relativedelta
from datetime import date, datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models, SUPERUSER_ID
import time
import itertools
import xlsxwriter
import re
import string

class BkpOkpXlsx(models.AbstractModel):
	_name = 'report.bmo_material_request.bkp_okp_xls'
	_description = 'Report BKB-OKP xls'
	_inherit = 'report.report_xlsx.abstract'

	def generate_xlsx_report(self, workbook, data, partners):
		PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
		BASE_DIR = os.path.dirname(PROJECT_ROOT)
		PATH_DIR = '/static/src/img/'
		FILE_DIR = BASE_DIR + PATH_DIR
		FILE_NAME = 'logo.png'

		for obj in partners:
			company_format = workbook.add_format(
				{'align': 'center', 'valign':'vcenter', 'font_name': 'Times New Roman', 'font_color': 'black', 'border': 1, 'bold': True})
			table_header = workbook.add_format(
				{'font_name': 'Times New Roman', 'align': 'center', 'font_size': 12,'font_color': 'black', 'border': 1, 'bold': True})

			table_row_left = workbook.add_format(
				{'font_name': 'Times New Roman', 'align': 'left', 'font_size': 12, 'border': 1})
			table_row_right = workbook.add_format(
				{'font_name': 'Times New Roman', 'align': 'center', 'font_size': 12, 'border': 1, 'bold': True})
			table_left = workbook.add_format(
				{'font_name': 'Times New Roman', 'align': 'left', 'border': 1, 'bold': True})
			table_center = workbook.add_format(
				{'font_name': 'Times New Roman', 'align': 'center', 'valign':'vcenter', 'border': 1, 'bold': True})

			worksheet = workbook.add_worksheet(obj.name)

			# set col width
			worksheet.set_column('A:A', 5)
			worksheet.set_column('B:B', 15)
			worksheet.set_column('C:C', 30)
			worksheet.set_column('D:D', 25)
			worksheet.set_column('E:E', 15)
			worksheet.set_column('F:F', 13)
			worksheet.set_column('G:G', 10)

			# worksheet.merge_range('A2:D5', '', company_format)
			# worksheet.insert_image('A2:D5', FILE_DIR+FILE_NAME, {'x_scale': 1.5, 'y_scale': 1.5, 'x_offset':20})
			
			worksheet.merge_range('A1:G1', 'BUKTI KIRIM BARANG  '+obj.name, company_format)
			worksheet.merge_range('A2:G2', 'ORDER KERJA PRODUKSI(BKB-OKP)', company_format)

# =========================================================================================        
			header = ["No","Item Code", "Item Description", "From", "Lot Number", "Exp Date", "Qty", "UOM"]
			sml = []
			lms = []
			no = 1
			if obj.move_line_ids_without_package:
				for detop in obj.move_line_ids_without_package:
					if detop.product_id.default_code not in lms:
						sml.append({
							"No"			   : str(no),
							"Item Code"		   : detop.product_id.default_code,
							"Item Description" : detop.product_id.name,
							"From"			   : detop.location_id.display_name,
							# "To"			   : detop.location_dest_id.display_name,
							"Lot Number"	   : detop.lot_id.name or '',
							"Exp Date"		   : detop.lot_id.expiration_date.strftime("%d-%b-%Y") if detop.lot_id.expiration_date else '',
							"Qty" 			   : detop.qty_done,
							"UOM" 			   : detop.product_uom_id.name,
						})
						lms.append(detop.product_id.default_code)
						no+=1
					else:
						sml.append({
							"No"			   : "",
							"Item Code"		   : '',
							"Item Description" : '',
							"From"			   : detop.location_id.display_name,
							# "To"			   : detop.location_dest_id.display_name,
							"Lot Number"	   : detop.lot_id.name or '',
							"Exp Date"		   : detop.lot_id.expiration_date.strftime("%d-%b-%Y") if detop.lot_id.expiration_date else '',
							"Qty" 			   : detop.qty_done,
							"UOM" 			   : detop.product_uom_id.name,
						})
			else:
				for op in obj.move_ids_without_package:
					sml.append({
						"No"			   : str(no),
						"Item Code"		   : op.product_id.default_code,
						"Item Description" : op.product_id.name,
						"From"			   : op.picking_id.location_id.display_name,
						# "To"			   : op.picking_id.location_dest_id.display_name,
						"Lot Number"	   : '-',
						"Exp Date"		   : '-',
						"Qty" 			   : op.quantity_done or 0,
						"UOM" 			   : op.product_uom.name,
					})
					# lms.append(detop.product_id.default_code)
					no+=1

			colh = -1
			for x in header:
				colh += 1
				worksheet.write(3, colh, x, table_header)
			
			no = 3;
			for line in sml:
				no += 1
				col = -1
				for i in header:
					col += 1
					worksheet.write(no, col, line[i], table_header)