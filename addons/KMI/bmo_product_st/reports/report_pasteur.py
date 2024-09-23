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


class DumpingXlsx(models.AbstractModel):
	_name = 'report.bmo_product_st.report_pasteur_xlsx'
	_description = 'Dumping Excell'
	_inherit = 'report.report_xlsx.abstract'

	def formating_styles(self,workbook):
		styles = dict()
		styles['company_format'] = workbook.add_format(
				{'align': 'center', 'valign':'vcenter','font_color': 'black', 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['table_header'] = workbook.add_format(
			{'align': 'center', 'font_size': 12,'font_color': 'black', 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', 'valign':'vcenter',})

		styles['table_row_left'] = workbook.add_format(
			{'align': 'left', 'font_size': 10, 'border': 1, 'text_wrap':True, 'font_name' : 'Times New Roman', 'valign':'vcenter',})
		styles['table_row_center'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'font_name' : 'Times New Roman', 'valign':'vcenter',})
		styles['table_row_right'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', 'valign':'vcenter',})
		styles['table_left'] = workbook.add_format(
			{'align': 'left', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', 'valign':'vcenter',})
		styles['table_center'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', 'valign':'vcenter',})
		styles['page_title'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'text_wrap':True, 'font_name' : 'Times New Roman', 'valign':'vcenter',})
		styles['space'] = workbook.add_format(
			{'border': 1, 'valign':'vcenter',})
		styles['keterangan'] = workbook.add_format(
			{'align': 'left', 'border': 1, 'bottom': 0, 'text_wrap':True, 'font_size': 10, 'font_name' : 'Times New Roman', 'valign':'vcenter',})
		styles['isi_keterangan'] = workbook.add_format(
			{'align': 'left', 'valign':'vcenter', 'border': 1, 'text_wrap':True, 'top': 0, 'font_size': 10, 'font_name' : 'Times New Roman', })
		return styles

	def get_next_cell(self, cell, row):
		split_cell = re.split('(\d+)', cell)
		# next_row =  str(int(split_cell[1]) + row) 
		next_cell = split_cell[0] + str(row)
		return next_cell

	def write_dictionary(self, x, n_row, worksheet, workbook, reset=False):
		cell_dict = {
			'A{row}'.format(row=n_row) : [x.number, self.formating_styles(workbook).get('table_row_center')],
			'B{row}:E{row}'.format(row=n_row) : [x.name, self.formating_styles(workbook).get('table_row_left')],
			'F{row}'.format(row=n_row) : [x.unit if x.unit else '', self.formating_styles(workbook).get('table_row_center')],
			'G{row}'.format(row=n_row) : [x.std if x.std else '', self.formating_styles(workbook).get('table_row_center')],
			'H{row}'.format(row=n_row) : [x.actual if x.actual else '', self.formating_styles(workbook).get('table_row_center')],
			# 'J{row}'.format(row=n_row) : [x.remark if x.remark else '', self.formating_styles(workbook).get('table_row_left')],
		}
		if reset:
			cell_dict = {
				'I{row}'.format(row=n_row) : [x.number, self.formating_styles(workbook).get('table_row_center')],
				'J{row}:M{row}'.format(row=n_row) : [x.name, self.formating_styles(workbook).get('table_row_left')],
				'N{row}'.format(row=n_row) : [x.unit if x.unit else '', self.formating_styles(workbook).get('table_row_center')],
				'O{row}'.format(row=n_row) : [x.std if x.std else '', self.formating_styles(workbook).get('table_row_center')],
				'P{row}'.format(row=n_row) : [x.actual if x.actual else '', self.formating_styles(workbook).get('table_row_center')],
				# 'T{row}'.format(row=n_row) : [x.remark if x.remark else '', self.formating_styles(workbook).get('table_row_left')],
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
		print(float_time)
		return '%02d:%02d' % (int(float_time), float_time % 1 * 60)

	def generate_xlsx_report(self, workbook, data, objects):
		PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
		BASE_DIR = os.path.dirname(PROJECT_ROOT)
		PATH_DIR = '/static/src/img/'
		FILE_DIR = BASE_DIR + PATH_DIR
		FILE_NAME = 'logo.png'
		for obj in objects:
			worksheet = workbook.add_worksheet(obj.name)
			worksheet.set_column('A:A',3.8) # number
			worksheet.set_column('B:E',6.6) # name
			worksheet.set_column('F:F',9.7) # unit
			worksheet.set_column('G:G',15) # std
			worksheet.set_column('H:H',6) # std
			worksheet.set_column('I:I',9.7) # value
			worksheet.set_column('J:J',18.2) # remarks

			worksheet.set_column('K:K',3.8)
			worksheet.set_column('L:O',6.6)
			worksheet.set_column('P:P',18.2)
			# worksheet.set_column('Q:R',6)
			# worksheet.set_column('S:S',15.2)
			# worksheet.set_column('T:T',18.2)

			worksheet.merge_range('A2:D4', '', self.formating_styles(workbook).get('company_format'))
			worksheet.insert_image('A2:D4', FILE_DIR+FILE_NAME, {'x_scale': 1, 'y_scale': 1, 'x_offset':20})
			
			worksheet.merge_range('E2:N2', 'QC DEPARTEMENT', self.formating_styles(workbook).get('company_format'))
			worksheet.merge_range('E3:N4', 'FORM PASTEURISASI ' + obj.product_id.display_name, self.formating_styles(workbook).get('company_format'))

			worksheet.write('O2', 'No Dok', self.formating_styles(workbook).get('table_left'))
			worksheet.write('O3', 'Tanggal', self.formating_styles(workbook).get('table_left'))
			worksheet.write('O4', 'Revisi: ', self.formating_styles(workbook).get('table_left'))
			worksheet.write('P2', ': ' + obj.name, self.formating_styles(workbook).get('table_left'))
			worksheet.write('P3', ': ' + obj.revision_date.strftime("%Y-%m-%d") if obj.revision_date else '', self.formating_styles(workbook).get('table_left'))
			worksheet.write('P4', ': ' + str(obj.revisi), self.formating_styles(workbook).get('table_left'))

			# Write Header of Report
			worksheet.merge_range('A5:D5', 'Hari / Tanggal', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('E5:F5', ': ' + obj.date.strftime("%d-%m-%Y") if obj.date else '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('A6:D6', 'Shift', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('E6:F6', ': ' + obj.shift if obj.shift else '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.write('G5', 'Batch', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('H5:I5', ': ' + obj.batch_id.okp_id.name if obj.batch_id else '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.write('G6', 'No BO', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('H6:I6', ': ' + obj.batch_id.number_ref if obj.batch_id else '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('J5:K5', 'Nama Produk', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('L5:P5', ': ' + obj.product_id.name if obj.product_id else '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('J6:K6', 'Team', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('L6:P6', ': ' + obj.team if obj.team else '', self.formating_styles(workbook).get('table_row_left'))

			# worksheet.merge_range('A7:T7', 'PROCESS MIXING', self.formating_styles(workbook).get('table_header'))

			# # Write Every Lines
			worksheet.write('A7', 'No.', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('B7:E7', 'URAIAN KEGIATAN', self.formating_styles(workbook).get('page_title'))
			worksheet.write('F7', 'Unit', self.formating_styles(workbook).get('page_title'))
			worksheet.write('G7', 'Std', self.formating_styles(workbook).get('page_title'))
			worksheet.write('H7', 'Value', self.formating_styles(workbook).get('page_title'))
			# worksheet.write('7', 'Remark', self.formating_styles(workbook).get('page_title'))
			worksheet.write('I7', 'No.', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('J7:M7', 'URAIAN KEGIATAN', self.formating_styles(workbook).get('page_title'))
			worksheet.write('N7', 'Unit', self.formating_styles(workbook).get('page_title'))
			worksheet.write('O7', 'Std', self.formating_styles(workbook).get('page_title'))
			worksheet.write('P7', 'Value', self.formating_styles(workbook).get('page_title'))
			f_row = 8
			n_row = f_row
			lrow = 1
			end_row = 0

			worksheet.merge_range('A{n_row}:H{n_row}'.format(n_row=n_row), obj.page_a_title, self.formating_styles(workbook).get('page_title'))
			n_row +=1
			for x in obj.preparation_ids:
				# if lrow < m_row:
				n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=False)

			n_row = f_row
			worksheet.merge_range('I{n_row}:P{n_row}'.format(n_row=n_row), obj.page_b_title, self.formating_styles(workbook).get('page_title'))
			n_row +=1

			for x in obj.preheating_ids:
				n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=True)
				# print(n_row)

			worksheet.merge_range('I{n_row}:P{end_row}'.format(n_row=n_row, end_row=n_row + 1), '', self.formating_styles(workbook).get('space'))
			# print()
			n_row += 2

			worksheet.merge_range('A{n_row}:H{n_row}'.format(n_row=n_row), obj.page_c_title, self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('I{n_row}:P{n_row}'.format(n_row=n_row), 'Actual Check', self.formating_styles(workbook).get('page_title'))
			n_row +=1

			worksheet.write('A{n_row}'.format(n_row=n_row), 'No.', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('B{n_row}:E{n_row}'.format(n_row=n_row), 'URAIAN KEGIATAN', self.formating_styles(workbook).get('page_title'))
			worksheet.write('F{n_row}'.format(n_row=n_row), 'Unit', self.formating_styles(workbook).get('page_title'))
			worksheet.write('G{n_row}'.format(n_row=n_row), 'Std', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('H{n_row}:I{n_row}'.format(n_row=n_row), 'Actual(0)', self.formating_styles(workbook).get('page_title'))
			worksheet.write('J{n_row}'.format(n_row=n_row), 'Actual(15)', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('K{n_row}:L{n_row}'.format(n_row=n_row), 'Actual(30)', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('M{n_row}:N{n_row}'.format(n_row=n_row), 'Actual(45)', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('O{n_row}:P{n_row}'.format(n_row=n_row), 'Actual(60)', self.formating_styles(workbook).get('page_title'))
			n_row += 1

			for x in obj.pasteurization_1_ids:
				worksheet.write('A{n_row}'.format(n_row=n_row), x.number, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('B{n_row}:E{n_row}'.format(n_row=n_row), x.name, self.formating_styles(workbook).get('table_row_left'))
				worksheet.write('F{n_row}'.format(n_row=n_row), x.unit, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('G{n_row}'.format(n_row=n_row), x.std, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('H{n_row}:I{n_row}'.format(n_row=n_row), x.actual_0 if x.actual_0 else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('J{n_row}'.format(n_row=n_row), x.actual_15 if x.actual_15 else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('K{n_row}:L{n_row}'.format(n_row=n_row), x.actual_30 if x.actual_30 else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('M{n_row}:N{n_row}'.format(n_row=n_row), x.actual_45 if x.actual_45 else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('O{n_row}:P{n_row}'.format(n_row=n_row), x.actual_60 if x.actual_60 else '', self.formating_styles(workbook).get('table_row_center'))
				n_row +=1

			for x in obj.pasteurization_2_ids:
				worksheet.write('A{n_row}'.format(n_row=n_row), x.number, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('B{n_row}:E{n_row}'.format(n_row=n_row), x.name, self.formating_styles(workbook).get('table_row_left'))
				worksheet.write('F{n_row}'.format(n_row=n_row), x.unit, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('G{n_row}'.format(n_row=n_row), x.std, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('H{n_row}:J{n_row}'.format(n_row=n_row), self._convert_to_time(round(float(x.pasteur_start),15)) if x.pasteur_start else '', self.formating_styles(workbook).get('table_row_center'))
				# worksheet.write('J{n_row}'.format(n_row=n_row), x.pasteur_finish if x.pasteur_finish else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('K{n_row}:L{n_row}'.format(n_row=n_row), 'Finish', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('M{n_row}:P{n_row}'.format(n_row=n_row), self._convert_to_time(round(float(x.pasteur_finish), 15)) if x.pasteur_finish else '', self.formating_styles(workbook).get('table_row_center'))
				# worksheet.merge_range('O{n_row}:P{n_row}'.format(n_row=n_row), x.actual_60 if x.actual_60 else '', self.formating_styles(workbook).get('table_row_center'))
				n_row +=1

			for x in obj.pasteurization_3_ids:
				worksheet.write('A{n_row}'.format(n_row=n_row), x.number, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('B{n_row}:E{n_row}'.format(n_row=n_row), x.name, self.formating_styles(workbook).get('table_row_left'))
				worksheet.write('F{n_row}'.format(n_row=n_row), x.unit, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('G{n_row}'.format(n_row=n_row), x.std, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('H{n_row}:P{n_row}'.format(n_row=n_row), x.actual if x.actual else '', self.formating_styles(workbook).get('table_row_center'))
				# worksheet.write('J{n_row}'.format(n_row=n_row), x.actual_15 if x.actual_15 else '', self.formating_styles(workbook).get('table_row_center'))
				# worksheet.merge_range('K{n_row}:L{n_row}'.format(n_row=n_row), x.actual_30 if x.actual_30 else '', self.formating_styles(workbook).get('table_row_center'))
				# worksheet.merge_range('M{n_row}:N{n_row}'.format(n_row=n_row), x.actual_45 if x.actual_45 else '', self.formating_styles(workbook).get('table_row_center'))
				# worksheet.merge_range('O{n_row}:P{n_row}'.format(n_row=n_row), x.actual_60 if x.actual_60 else '', self.formating_styles(workbook).get('table_row_center'))
				n_row +=1

			for x in obj.pasteurization_4_ids:
				worksheet.write('A{n_row}'.format(n_row=n_row), x.number, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('B{n_row}:E{n_row}'.format(n_row=n_row), x.name, self.formating_styles(workbook).get('table_row_left'))
				worksheet.write('F{n_row}'.format(n_row=n_row), x.unit, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('G{n_row}'.format(n_row=n_row), x.std, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('H{n_row}:P{n_row}'.format(n_row=n_row), x.actual if x.actual else '', self.formating_styles(workbook).get('table_row_center'))
				n_row +=1

			for x in obj.pasteurization_5_ids:
				worksheet.write('A{n_row}'.format(n_row=n_row), x.number, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('B{n_row}:E{n_row}'.format(n_row=n_row), x.name, self.formating_styles(workbook).get('table_row_left'))
				worksheet.write('F{n_row}'.format(n_row=n_row), x.unit, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('G{n_row}'.format(n_row=n_row), x.std, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('H{n_row}:J{n_row}'.format(n_row=n_row), self._convert_to_time(round(x.pasteur_start,15)) if x.pasteur_start else '', self.formating_styles(workbook).get('table_row_center'))
				# worksheet.write('J{n_row}'.format(n_row=n_row), x.pasteur_finish if x.pasteur_finish else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('K{n_row}:L{n_row}'.format(n_row=n_row), 'Finish', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('M{n_row}:P{n_row}'.format(n_row=n_row), self._convert_to_time(round(x.pasteur_finish, 15)) if x.pasteur_finish else '', self.formating_styles(workbook).get('table_row_center'))
				# worksheet.merge_range('O{n_row}:P{n_row}'.format(n_row=n_row), x.actual_60 if x.actual_60 else '', self.formating_styles(workbook).get('table_row_center'))
				n_row +=1

			worksheet.merge_range('A{n_row}:P{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			n_row +=1

			for x in obj.quality_analysis_ids:
				worksheet.write('A{n_row}'.format(n_row=n_row), x.number, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('B{n_row}:E{n_row}'.format(n_row=n_row), x.name, self.formating_styles(workbook).get('table_row_left'))
				worksheet.write('F{n_row}'.format(n_row=n_row), x.unit, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('G{n_row}'.format(n_row=n_row), x.std, self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('H{n_row}:P{n_row}'.format(n_row=n_row), x.actual if x.actual else '', self.formating_styles(workbook).get('table_row_center'))
				n_row +=1

			worksheet.merge_range('A{n_row}:P{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			n_row +=1
			worksheet.merge_range('A{n_row}:P{n_row}'.format(n_row=n_row), 
				'Jika terjadi Trouble dan produk tertahan di ST selama lebih dari 2 jam. maka lakukan pengecekan suhu pada kolom berikut:', self.formating_styles(workbook).get('table_row_left'))
			n_row +=1
			worksheet.merge_range('A{n_row}:A{n_row2}'.format(n_row=n_row, n_row2=n_row +1), 'ST No', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('B{n_row}:P{n_row}'.format(n_row=n_row), 'Suhu (°C) jam ke-', self.formating_styles(workbook).get('page_title'))
			n_row +=1
			worksheet.write('B{n_row}'.format(n_row=n_row), '2', self.formating_styles(workbook).get('page_title'))
			worksheet.write('C{n_row}'.format(n_row=n_row), '4', self.formating_styles(workbook).get('page_title'))
			worksheet.write('D{n_row}'.format(n_row=n_row), '6', self.formating_styles(workbook).get('page_title'))
			worksheet.write('E{n_row}'.format(n_row=n_row), '8', self.formating_styles(workbook).get('page_title'))
			worksheet.write('F{n_row}'.format(n_row=n_row), '10', self.formating_styles(workbook).get('page_title'))
			worksheet.write('G{n_row}'.format(n_row=n_row), '12', self.formating_styles(workbook).get('page_title'))
			worksheet.write('H{n_row}'.format(n_row=n_row), '14', self.formating_styles(workbook).get('page_title'))
			worksheet.write('I{n_row}'.format(n_row=n_row), '16', self.formating_styles(workbook).get('page_title'))
			worksheet.write('J{n_row}'.format(n_row=n_row), '18', self.formating_styles(workbook).get('page_title'))
			worksheet.write('K{n_row}'.format(n_row=n_row), '20', self.formating_styles(workbook).get('page_title'))
			worksheet.write('L{n_row}'.format(n_row=n_row), '22', self.formating_styles(workbook).get('page_title'))
			worksheet.write('M{n_row}'.format(n_row=n_row), '24', self.formating_styles(workbook).get('page_title'))
			worksheet.write('N{n_row}'.format(n_row=n_row), '26', self.formating_styles(workbook).get('page_title'))
			worksheet.write('O{n_row}'.format(n_row=n_row), '28', self.formating_styles(workbook).get('page_title'))
			worksheet.write('P{n_row}'.format(n_row=n_row), '30', self.formating_styles(workbook).get('page_title'))
			n_row +=1
			for x in obj.st_no_ids:
				worksheet.write('A{n_row}'.format(n_row=n_row), x.st_no, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('B{n_row}'.format(n_row=n_row), x.suhu_jam_2, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('C{n_row}'.format(n_row=n_row), x.suhu_jam_4, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('D{n_row}'.format(n_row=n_row), x.suhu_jam_6, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('E{n_row}'.format(n_row=n_row), x.suhu_jam_8, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('F{n_row}'.format(n_row=n_row), x.suhu_jam_10, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('G{n_row}'.format(n_row=n_row), x.suhu_jam_12, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('H{n_row}'.format(n_row=n_row), x.suhu_jam_14, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('I{n_row}'.format(n_row=n_row), x.suhu_jam_16, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('J{n_row}'.format(n_row=n_row), x.suhu_jam_18, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('K{n_row}'.format(n_row=n_row), x.suhu_jam_20, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('L{n_row}'.format(n_row=n_row), x.suhu_jam_22, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('M{n_row}'.format(n_row=n_row), x.suhu_jam_24, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('N{n_row}'.format(n_row=n_row), x.suhu_jam_26, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('O{n_row}'.format(n_row=n_row), x.suhu_jam_28, self.formating_styles(workbook).get('table_row_center'))
				worksheet.write('P{n_row}'.format(n_row=n_row), x.suhu_jam_30, self.formating_styles(workbook).get('table_row_center'))
				n_row +=1

			worksheet.merge_range('A{n_row}:P{n_row2}'.format(n_row=n_row,n_row2=n_row+1), 'CATATAN : {}'.format(obj.note), self.formating_styles(workbook).get('table_row_left'))
			n_row +=2
			worksheet.merge_range('A{n_row}:H{end_row}'.format(n_row=n_row, end_row=n_row), 'Keterangan:', self.formating_styles(workbook).get('keterangan'))
			worksheet.merge_range('A{n_row}:H{end_row}'.format(n_row=n_row+1, end_row=n_row + 6), obj.ket, self.formating_styles(workbook).get('isi_keterangan'))
			worksheet.merge_range('I{n_row}:J{end_row}'.format(n_row=n_row, end_row=n_row), 'Tekanan Chiller max 1.5 bar', self.formating_styles(workbook).get('keterangan'))
			worksheet.merge_range('I{n_row}:J{end_row}'.format(n_row=n_row+1, end_row=n_row + 6), obj.tekanan, self.formating_styles(workbook).get('isi_keterangan'))
			worksheet.merge_range('K{n_row}:N{end_row}'.format(n_row=n_row, end_row=n_row + 5), '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('O{n_row}:P{end_row}'.format(n_row=n_row, end_row=n_row + 5), '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('K{n_row}:N{end_row}'.format(n_row=n_row+6, end_row=n_row + 6), 'Operator: {}'.format(obj.operator if obj.operator else ''), self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('O{n_row}:P{end_row}'.format(n_row=n_row+6, end_row=n_row + 6), 'Supervisor/Leader: {}'.format(obj.leader if obj.leader else '') , self.formating_styles(workbook).get('table_row_left'))