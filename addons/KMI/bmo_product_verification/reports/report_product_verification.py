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

class UnLoaderXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_product_verification'
	_description = 'Daily Report Product Verification'
	_inherit = 'report.report_xlsx.abstract'

	def formating_styles(self,workbook):
		styles = dict()
		styles['company_format'] = workbook.add_format(
				{'align': 'center', 'valign':'vcenter','font_color': 'black', 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['table_header'] = workbook.add_format(
			{'align': 'center', 'font_size': 12,'font_color': 'black', 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })

		styles['table_row_left'] = workbook.add_format(
			{'align': 'left', 'font_size': 10, 'border': 1, 'text_wrap':True, 'font_name' : 'Times New Roman', })
		styles['table_row_center'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'valign':'vcenter', 'font_name' : 'Times New Roman', })
		styles['table_row_right'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['table_left'] = workbook.add_format(
			{'align': 'left', 'font_size': 10, 'border': 1, 'valign':'vcenter', 'bold': True, 'font_name' : 'Times New Roman', })
		styles['table_center'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'valign':'vcenter', 'text_wrap':True, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['page_title'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['space'] = workbook.add_format(
			{'border': 1,})
		styles['keterangan'] = workbook.add_format(
			{'align': 'left', 'valign':'top', 'border': 1, 'bold': True, 'bottom': 0, 'text_wrap':True, 'font_size': 10, 'font_name' : 'Times New Roman', })
		styles['isi_keterangan'] = workbook.add_format(
			{'align': 'left', 'valign':'top', 'border': 1, 'bold': True, 'top': 0, 'text_wrap':True, 'font_size': 10, 'font_name' : 'Times New Roman', })
		styles['table_row_center_blue'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'valign':'vcenter', 'font_name' : 'Times New Roman', 'bg_color': '#4b97d1'})
		styles['table_row_center_yellow'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'valign':'vcenter', 'font_name' : 'Times New Roman', 'bg_color': '#F4E638'})
		styles['table_row_center_red'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'valign':'vcenter', 'font_name' : 'Times New Roman', 'bg_color': '#F84A67'})
		return styles

	def get_next_cell(self, cell, row):
		split_cell = re.split('(\d+)', cell)
		# next_row =  str(int(split_cell[1]) + row) 
		next_cell = split_cell[0] + str(row)
		return next_cell

	def write_dictionary(self, x, n_row, worksheet, workbook, grid):
		cell_dict = {}
		get_color = {
			x.color == 'primary' : 'table_row_center_blue',
			x.color == 'danger' : 'table_row_center_red',
			x.color == 'warning' : 'table_row_center_yellow',
			x.color == False : 'table_row_center',
		}
		if grid == 1:
			cell_dict = {
				'A{row}'.format(row=n_row) : [x.number or '', self.formating_styles(workbook).get('table_row_center')],
				'B{row}'.format(row=n_row) : ["{:.2f}".format(x.weight) or '', self.formating_styles(workbook).get('table_row_center')],
				'C{row}'.format(row=n_row) : ["{:.2f}".format(x.volume) or '', self.formating_styles(workbook).get(get_color.get(True))],
				'D{row}'.format(row=n_row) : [x.kekuatan_seal or '', self.formating_styles(workbook).get('table_row_center')],
				'E{row}'.format(row=n_row) : [x.visual_check or '', self.formating_styles(workbook).get('table_row_center')],
			}
		elif grid == 2:
			cell_dict = {
				'F{row}'.format(row=n_row) : [x.number or '', self.formating_styles(workbook).get('table_row_center')],
				'G{row}'.format(row=n_row) : ["{:.2f}".format(x.weight) or '', self.formating_styles(workbook).get('table_row_center')],
				'H{row}'.format(row=n_row) : ["{:.2f}".format(x.volume) or '', self.formating_styles(workbook).get(get_color.get(True))],
				'I{row}'.format(row=n_row) : [x.kekuatan_seal or '', self.formating_styles(workbook).get('table_row_center')],
				'J{row}'.format(row=n_row) : [x.visual_check or '', self.formating_styles(workbook).get('table_row_center')],
			}
		elif grid == 3:
			cell_dict = {
				'K{row}'.format(row=n_row) : [x.number or '', self.formating_styles(workbook).get('table_row_center')],
				'L{row}'.format(row=n_row) : ["{:.2f}".format(x.weight) or '', self.formating_styles(workbook).get('table_row_center')],
				'M{row}'.format(row=n_row) : ["{:.2f}".format(x.volume) or '', self.formating_styles(workbook).get(get_color.get(True))],
				'N{row}'.format(row=n_row) : [x.kekuatan_seal or '', self.formating_styles(workbook).get('table_row_center')],
				'O{row}'.format(row=n_row) : [x.visual_check or '', self.formating_styles(workbook).get('table_row_center')],
			}

		for key, value in cell_dict.items():
			key_split = key.split(':')
			if len(key_split) == 1:
				w_key = self.get_next_cell(key, n_row)
				worksheet.write(w_key, value[0], value[1])
			else:
				w_key = ':'.join(self.get_next_cell(k, n_row) for k in key_split)
				worksheet.merge_range(w_key, value[0], value[1])
			# print(value)
		n_row +=1
		return n_row

	def _convert_to_time(self, float_time):
		return '%02d:%02d' % (int(float_time), float_time % 1 * 60)

	def generate_xlsx_report(self, workbook, data, objects):
		PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
		BASE_DIR = os.path.dirname(PROJECT_ROOT)
		PATH_DIR = '/static/src/img/'
		FILE_DIR = BASE_DIR + PATH_DIR
		FILE_NAME = 'logo.png'

		for obj in objects:
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
			worksheet.set_column('A:A', 12)
			worksheet.set_column('B:B', 10)
			worksheet.set_column('C:C', 12)
			worksheet.set_column('D:D', 7.5)
			worksheet.set_column('E:E', 7.5)
			worksheet.set_column('F:F', 12)
			worksheet.set_column('G:G', 10)
			worksheet.set_column('H:H', 12)
			worksheet.set_column('I:I', 7.5)
			worksheet.set_column('J:J', 7.5)
			worksheet.set_column('K:K', 12)
			worksheet.set_column('L:L', 10)
			worksheet.set_column('M:M', 12)
			worksheet.set_column('N:N', 7.5)
			worksheet.set_column('O:O', 7.5)

			worksheet.merge_range('A2:C5', '', self.formating_styles(workbook).get('company_format'))
			worksheet.insert_image('A2:C5', FILE_DIR+FILE_NAME, {'x_scale': 1.3, 'y_scale': 1.3, 'x_offset':20})
			
			worksheet.merge_range('D2:L3', 'QC DEPARTEMENT', self.formating_styles(workbook).get('company_format'))
			worksheet.merge_range('D4:L5', 'INLINE PRODUCT VERIFICATION ', self.formating_styles(workbook).get('company_format'))

			worksheet.write('M2', 'No Dok', self.formating_styles(workbook).get('table_left'))
			worksheet.write('M3', 'Tanggal', self.formating_styles(workbook).get('table_left'))
			worksheet.write('M4', 'Hal', self.formating_styles(workbook).get('table_left'))
			worksheet.write('M5', 'Revisi', self.formating_styles(workbook).get('table_left'))

			worksheet.merge_range('N2:O2', ': {}'.format(obj.name), self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('N3:O3', ': {}'.format(obj.release_date.strftime("%d-%m-%Y")), self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('N4:O4', ': ', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('N5:O5', ': {}'.format(obj.revisi), self.formating_styles(workbook).get('table_left'))

			worksheet.merge_range('A6:O6', '', self.formating_styles(workbook).get('space'))
# =========================================================================================        
			n_row = 7
			worksheet.write('A{row}'.format(row=n_row), 'Product', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('B{row}:E{row}'.format(row=n_row), obj.product_id.name or '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('F{row}:G{row}'.format(row=n_row), 'Speed Filling', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('H{row}:J{row}'.format(row=n_row), obj.speed_filling or '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('K{row}:L{row}'.format(row=n_row), 'Type Of Bottle', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('M{row}:O{row}'.format(row=n_row), obj.bottle_id.display_name or '', self.formating_styles(workbook).get('table_row_left'))
			n_row += 1

			worksheet.write('A{row}'.format(row=n_row), 'OKP', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('B{row}:E{row}'.format(row=n_row), obj.okp_id.display_name or '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('F{row}:G{row}'.format(row=n_row), 'Metode Uji Kekuatan', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('H{row}:J{row}'.format(row=n_row), dict(obj._fields['metode_uji'].selection).get(obj.metode_uji) or '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('K{row}:L{row}'.format(row=n_row), 'Prod Date', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('M{row}:O{row}'.format(row=n_row), obj.production_date.strftime("%d-%b-%Y") if obj.production_date else '', self.formating_styles(workbook).get('table_row_left'))
			n_row +=1

			worksheet.write('A{row}'.format(row=n_row), 'Batch', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('B{row}:E{row}'.format(row=n_row), obj.batch_no or '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('F{row}:G{row}'.format(row=n_row), 'Weight Tare (g)', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('H{row}:J{row}'.format(row=n_row),  obj.weight_tare or '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('K{row}:L{row}'.format(row=n_row), 'SG (g/mL)', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('M{row}:O{row}'.format(row=n_row), obj.specific_gravity or '', self.formating_styles(workbook).get('table_row_left'))
			n_row +=1

# ======================================================================================================================
			
			# Merge 2 Baris
			worksheet.merge_range('A{row}:A{row2}'.format(row=n_row,row2=n_row+1), 'Nozzle', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('F{row}:F{row2}'.format(row=n_row,row2=n_row+1), 'Nozzle', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('K{row}:K{row2}'.format(row=n_row,row2=n_row+1), 'Nozzle', self.formating_styles(workbook).get('table_center'))

			worksheet.merge_range('D{row}:D{row2}'.format(row=n_row,row2=n_row+1), 'Kekuatan Seal', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('I{row}:I{row2}'.format(row=n_row,row2=n_row+1), 'Kekuatan Seal', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('N{row}:N{row2}'.format(row=n_row,row2=n_row+1), 'Kekuatan Seal', self.formating_styles(workbook).get('table_center'))

			worksheet.merge_range('E{row}:E{row2}'.format(row=n_row,row2=n_row+1), 'Visual Check', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('J{row}:J{row2}'.format(row=n_row,row2=n_row+1), 'Visual Check', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('O{row}:O{row2}'.format(row=n_row,row2=n_row+1), 'Visual Check', self.formating_styles(workbook).get('table_center'))

			# Tanpa Merge
			worksheet.write('B{row}'.format(row=n_row), 'Std Volume', self.formating_styles(workbook).get('table_center'))
			worksheet.write('C{row}'.format(row=n_row), obj.std_volume or '', self.formating_styles(workbook).get('table_center'))

			worksheet.write('G{row}'.format(row=n_row), 'Std Volume', self.formating_styles(workbook).get('table_center'))
			worksheet.write('H{row}'.format(row=n_row), obj.std_volume or '', self.formating_styles(workbook).get('table_center'))

			worksheet.write('L{row}'.format(row=n_row), 'Std Volume', self.formating_styles(workbook).get('table_center'))
			worksheet.write('M{row}'.format(row=n_row), obj.std_volume or '', self.formating_styles(workbook).get('table_center'))

			n_row += 1

			worksheet.write('B{row}'.format(row=n_row), 'Weight (g)', self.formating_styles(workbook).get('table_center'))
			worksheet.write('C{row}'.format(row=n_row), 'Volume (mL)', self.formating_styles(workbook).get('table_center'))

			worksheet.write('G{row}'.format(row=n_row), 'Weight (g)', self.formating_styles(workbook).get('table_center'))
			worksheet.write('H{row}'.format(row=n_row), 'Volume (mL)', self.formating_styles(workbook).get('table_center'))

			worksheet.write('L{row}'.format(row=n_row), 'Weight (g)', self.formating_styles(workbook).get('table_center'))
			worksheet.write('M{row}'.format(row=n_row), 'Volume (mL)', self.formating_styles(workbook).get('table_center'))

			n_row += 1

			# PENCETAKAN VERIFICATION PRODUCT LINE
			f_row = n_row
			for x in obj.verification_product_1_line:
				n_row = self.write_dictionary(x, n_row, worksheet, workbook, 1)

			n_row = f_row
			for x in obj.verification_product_2_line:
				n_row = self.write_dictionary(x, n_row, worksheet, workbook, 2)

			n_row = f_row
			for x in obj.verification_product_3_line:
				n_row = self.write_dictionary(x, n_row, worksheet, workbook, 3)

# ======================================================================================================================


			worksheet.write('A{row}'.format(row=n_row), 'Max', self.formating_styles(workbook).get('table_center'))
			worksheet.write('F{row}'.format(row=n_row), 'Max', self.formating_styles(workbook).get('table_center'))
			worksheet.write('K{row}'.format(row=n_row), 'Max', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D{row}:E{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))
			worksheet.merge_range('I{row}:J{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))
			worksheet.merge_range('N{row}:O{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))

			worksheet.write('B{row}'.format(row=n_row), "{:.2f}".format(obj.max_weight_1) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('C{row}'.format(row=n_row), "{:.2f}".format(obj.max_volume_1) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('G{row}'.format(row=n_row), "{:.2f}".format(obj.max_weight_2) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('H{row}'.format(row=n_row), "{:.2f}".format(obj.max_volume_2) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('L{row}'.format(row=n_row), "{:.2f}".format(obj.max_weight_3) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('M{row}'.format(row=n_row), "{:.2f}".format(obj.max_volume_3) or '', self.formating_styles(workbook).get('table_row_center'))
			n_row += 1

			worksheet.write('A{row}'.format(row=n_row), 'Min', self.formating_styles(workbook).get('table_center'))
			worksheet.write('F{row}'.format(row=n_row), 'Min', self.formating_styles(workbook).get('table_center'))
			worksheet.write('K{row}'.format(row=n_row), 'Min', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D{row}:E{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))
			worksheet.merge_range('I{row}:J{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))
			worksheet.merge_range('N{row}:O{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))

			worksheet.write('B{row}'.format(row=n_row), "{:.2f}".format(obj.min_weight_1) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('C{row}'.format(row=n_row), "{:.2f}".format(obj.min_volume_1) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('G{row}'.format(row=n_row), "{:.2f}".format(obj.min_weight_2) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('H{row}'.format(row=n_row), "{:.2f}".format(obj.min_volume_2) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('L{row}'.format(row=n_row), "{:.2f}".format(obj.min_weight_3) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('M{row}'.format(row=n_row), "{:.2f}".format(obj.min_volume_3) or '', self.formating_styles(workbook).get('table_row_center'))
			n_row += 1

			worksheet.write('A{row}'.format(row=n_row), 'Average', self.formating_styles(workbook).get('table_center'))
			worksheet.write('F{row}'.format(row=n_row), 'Average', self.formating_styles(workbook).get('table_center'))
			worksheet.write('K{row}'.format(row=n_row), 'Average', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D{row}:E{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))
			worksheet.merge_range('I{row}:J{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))
			worksheet.merge_range('N{row}:O{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))

			worksheet.write('B{row}'.format(row=n_row), "{:.2f}".format(obj.average_weight_1) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('C{row}'.format(row=n_row), "{:.2f}".format(obj.average_volume_1) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('G{row}'.format(row=n_row), "{:.2f}".format(obj.average_weight_2) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('H{row}'.format(row=n_row), "{:.2f}".format(obj.average_volume_2) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('L{row}'.format(row=n_row), "{:.2f}".format(obj.average_weight_3) or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('M{row}'.format(row=n_row), "{:.2f}".format(obj.average_volume_3) or '', self.formating_styles(workbook).get('table_row_center'))
			n_row += 1

			worksheet.write('A{row}'.format(row=n_row), 'PIC Analisa', self.formating_styles(workbook).get('table_center'))
			worksheet.write('F{row}'.format(row=n_row), 'PIC Analisa', self.formating_styles(workbook).get('table_center'))
			worksheet.write('K{row}'.format(row=n_row), 'PIC Analisa', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D{row}:E{row}'.format(row=n_row), obj.pic_analisa or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('I{row}:J{row}'.format(row=n_row), obj.pic_analisa or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('N{row}:O{row}'.format(row=n_row), obj.pic_analisa or '', self.formating_styles(workbook).get('table_row_center'))

			n_row += 1

			# worksheet.write('A{row}'.format(row=n_row), 'Jam Analisa', self.formating_styles(workbook).get('table_center'))
			# worksheet.write('F{row}'.format(row=n_row), 'Jam Analisa', self.formating_styles(workbook).get('table_center'))
			# worksheet.write('K{row}'.format(row=n_row), 'Jam Analisa', self.formating_styles(workbook).get('table_center'))
			# worksheet.merge_range('D{row}:E{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))
			# worksheet.merge_range('I{row}:J{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))
			# worksheet.merge_range('N{row}:O{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))

			# n_row += 1

			# KOLOM TANDA TANGAN
			worksheet.merge_range('A{row}:E{row}'.format(row=n_row), 'Catatan', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('F{row}:H{row}'.format(row=n_row), 'Diperiksa Oleh', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('I{row}:K{row}'.format(row=n_row), 'Disetujui Oleh', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('L{row}:O{row}'.format(row=n_row), 'Kesimpulan', self.formating_styles(workbook).get('table_left'))
			n_row += 1

			worksheet.merge_range('A{row}:E{lrow}'.format(row=n_row, lrow=n_row+4), obj.note or '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('F{row}:H{lrow}'.format(row=n_row,lrow=n_row+3), '', self.formating_styles(workbook).get('space'))
			worksheet.merge_range('I{row}:K{lrow}'.format(row=n_row,lrow=n_row+3), '', self.formating_styles(workbook).get('space'))
			worksheet.merge_range('F{row}:H{row}'.format(row=n_row+4), '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('I{row}:K{row}'.format(row=n_row+4), obj.tgl_setuju.strftime("%d-%b-%Y") if obj.tgl_setuju else '', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('L{row}:O{lrow}'.format(row=n_row,lrow=n_row+4), obj.kesimpulan or '', self.formating_styles(workbook).get('table_row_center'))

			n_row += 4