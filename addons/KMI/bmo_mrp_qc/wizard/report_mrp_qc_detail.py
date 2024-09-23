# -*- coding: utf-8 -*-

from email.policy import default
import io
import os
import base64
from dateutil import relativedelta
from datetime import date, datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _, SUPERUSER_ID
import time
import itertools
import xlsxwriter
import re
import string

class QcDetXlsx(models.AbstractModel):
	_name = 'report.bmo_mrp_qc.report_mrp_qc_detail'
	_description = ''
	_inherit = 'report.report_xlsx.abstract'

	def generate_xlsx_report(self, workbook, data, partners):
		PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
		BASE_DIR = os.path.dirname(PROJECT_ROOT)
		PATH_DIR = '/static/src/img/'
		FILE_DIR = BASE_DIR + PATH_DIR
		FILE_NAME = 'logo.png'

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
		table_left_no_border = workbook.add_format(
			{'font_name': 'Times New Roman', 'align': 'left', 'bold': True})
		table_center = workbook.add_format(
			{'font_name': 'Times New Roman', 'align': 'center', 'valign':'vcenter', 'border': 1, 'bold': True})
		line_format = workbook.add_format(
			{'align': 'center', 'valign':'vcenter', 'font_name': 'Times New Roman', 'font_color': 'black',\
			 'border': 1, 'bold': True, 'num_format': '#,##0.00'}) 
		worksheet = workbook.add_worksheet('obj.name')

		# set col width
		worksheet.set_column('A:A', 17)
		worksheet.set_column('B:B', 15)
		worksheet.set_column('C:C', 15)
		worksheet.set_column('D:D', 30)
		worksheet.set_column('E:E', 15)
		worksheet.set_column('F:F', 15)
		worksheet.set_column('G:G', 15)
		worksheet.set_column('H:H', 15)
		worksheet.set_column('I:I', 15)
		worksheet.set_column('J:J', 15)
		worksheet.set_column('K:K', 15)
		worksheet.set_column('L:L', 15)
		worksheet.set_column('M:M', 15)
		worksheet.set_column('N:N', 15)

		judul = "FORM HASIL ANALISA FISIKA KIMIA DAN MIKROBIOLOGI"
		header = ["Item Code", "Lot Number", "Batch / Retort", "Test Parameter", "Test Class",\
					"Test Unit", "Value Char", "Min Value Num", "Max Value Num", "Result Value"]    
					
		validasi_okp = [x.number_batch_proses_id.okp_id.id for x in partners]
		# print('============ validasi', partners.tipe_category if partners.tipe_category else 'kosong')
		if len(set(validasi_okp)) >= 2:
		# 	if validasi.count(validasi[0]) < 1 :
			raise ValidationError(_('OKP Tidak Sama'))

		no_doc = [x.name for x in partners]
		master_data_date = [x.master_qc_id.date for x in partners] 
		master_data_version = [x.master_qc_id.version for x in partners]
		prod_name = [x.product_id.display_name for x in partners]
		prod_code = [x.product_id.default_code for x in partners] 
		lot = [x.lot_producing_id.name for x in partners if x.lot_producing_id or ''] 
		pro_name = [x.product_id.name for x in partners]

		worksheet.merge_range('A1:B4', '', company_format)
		worksheet.insert_image('A1:B4', FILE_DIR+FILE_NAME, {'x_scale': 1.5, 'y_scale': 1.5, 'x_offset':20})
		
		worksheet.merge_range('C1:H1', 'QC DEPARTMENT', company_format)
		worksheet.merge_range('C2:H3', judul, company_format)
		worksheet.merge_range('C4:H4', 'FINISHED GOODS INSPECTION ' + pro_name[0], company_format)

		worksheet.write('I1', 'No Dokumen ', table_left)
		worksheet.write('I2', 'Tanggal ', table_left)
		worksheet.write('I3', 'Hal ', table_left)
		worksheet.write('I4', 'Revisi ', table_left)

		worksheet.write('J1', ': '+ no_doc[0], table_left)
		worksheet.write('J2', ': '+ master_data_date[0].strftime('%d/%m/%Y'), table_left)
		worksheet.write('J3', ': 1/1', table_left)
		worksheet.write('J4', ': '+ master_data_version[0], table_left)

		worksheet.write('A6', 'Analysis Date ', table_left_no_border)
		worksheet.write('A7', 'Production Date ', table_left_no_border)
		worksheet.write('A8', 'Item Description ', table_left_no_border)
		worksheet.write('A9', 'Item Code ', table_left_no_border)
		worksheet.write('A10', 'Lot Number/BO ', table_left_no_border)
		worksheet.write('A11', 'Batch Number ', table_left_no_border)
		worksheet.write('A12', 'PIC ', table_left_no_border)
		worksheet.write('A13', 'Note ', table_left_no_border)

		worksheet.write('B6', ': ', table_left_no_border)
		worksheet.write('B7', ': '+ partners.production_date.strftime('%d/%m/%Y') if len(no_doc)<2 else '', table_left_no_border)
		worksheet.write('B8', ': '+ prod_name[0], table_left_no_border)
		worksheet.write('B9', ': '+ prod_code[0], table_left_no_border)
		worksheet.write('B10', ': '+ lot[0] if lot else '', table_left_no_border)
		worksheet.write('B11', ': '+ partners.number_batch_proses_id.display_name if len(no_doc)<2 else '', table_left_no_border)
		worksheet.write('B12', ': ', table_left_no_border)
		worksheet.write('B13', ': '+ partners.note if len(no_doc)<2 and partners.note else '' , table_left_no_border)

		worksheet.write('C6', 'PHYSICAL/CHEMICAL ', table_left_no_border)
		worksheet.write('C12', 'PHYSICAL/CHEMICAL ', table_left_no_border)

		worksheet.write('D6', ': '+ partners.date_physical.strftime('%d/%m/%Y') if len(no_doc)<2 and partners.date_physical else '', table_left_no_border)
		worksheet.write('D12', ': '+ partners.pic_physical if len(no_doc)<2 and partners.pic_physical else '', table_left_no_border)

		worksheet.write('E6', 'MICRO ', table_left_no_border)
		worksheet.write('E12', 'MICRO ', table_left_no_border)

		worksheet.write('F6', ': '+ partners.date_micro.strftime('%d/%m/%Y') if len(no_doc)<2 and partners.date_micro else '', table_left_no_border)
		worksheet.write('F12', ': '+ partners.pic_micro if len(no_doc)<2 and partners.pic_micro else '', table_left_no_border)
		qce = []
		num = ['0','1','2','3','4','5','6','7','8','9']
		for mrp in partners:

			for line in mrp.mrp_qc_lines:
				if line.result_value:
					if line.result_value[0] in num:
						reval = float(line.result_value)
					else:
						reval = line.result_value
				else:
					reval = ''

				qce.append({
					'Item Code': line.code or '',
					'Lot Number': line.lot_producing_id.name or '',
					'Batch / Retort': line.batch or '',
					'Test Parameter': line.name or '',
					'Test Class': line.test_calss or '',
					'Test Unit': line.unit or '',
					'Value Char': line.value_char or '',
					'Min Value Num': float(line.min_value_num) or '',
					'Max Value Num': float(line.max_value_num) or '',
					'Result Value': reval,
				})
                                                          
		colh = 0
		for x in header:
			worksheet.write(14, colh, x, company_format)
			colh += 1
		
		no = 14
		for line in qce:
			no += 1
			col = 0
			for i in header:
				worksheet.write(no, col, line[i], company_format)
				col += 1