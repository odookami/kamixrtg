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
	_name = 'report.bmo_dumping.report_dumping_xlsx'
	_description = 'Dumping Excell'
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
			{'align': 'center', 'font_size': 10, 'border': 1, 'font_name' : 'Times New Roman', })
		styles['table_row_right'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['table_left'] = workbook.add_format(
			{'align': 'left', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['table_center'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['page_title'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['space'] = workbook.add_format(
			{'border': 1,})
		styles['keterangan'] = workbook.add_format(
			{'align': 'left', 'border': 1, 'bottom': 0, 'text_wrap':True, 'font_size': 10, 'font_name' : 'Times New Roman', })
		styles['isi_keterangan'] = workbook.add_format(
			{'align': 'left', 'valign':'vcenter', 'border': 1, 'top': 0, 'font_size': 10, 'font_name' : 'Times New Roman', })
		return styles

	def get_next_cell(self, cell, row):
		split_cell = re.split('(\d+)', cell)
		# next_row =  str(int(split_cell[1]) + row) 
		next_cell = split_cell[0] + str(row)
		return next_cell

	def write_dictionary(self, x, n_row, worksheet, workbook, reset=False):
		cell_dict = {
			'A{row}'.format(row=n_row) : [x.number, self.formating_styles(workbook).get('table_row_center')],
			'B{row}:F{row}'.format(row=n_row) : [x.name, self.formating_styles(workbook).get('table_row_left')],
			'G{row}'.format(row=n_row) : [x.unit if x.unit else '', self.formating_styles(workbook).get('table_row_center')],
			'H{row}'.format(row=n_row) : [x.std if x.std else '', self.formating_styles(workbook).get('table_row_center')],
			'I{row}'.format(row=n_row) : [x.value if x.value else '', self.formating_styles(workbook).get('table_row_center')],
			'J{row}'.format(row=n_row) : [x.remark if x.remark else '', self.formating_styles(workbook).get('table_row_left')],
		}
		if reset:
			cell_dict = {
				'K{row}'.format(row=n_row) : [x.number, self.formating_styles(workbook).get('table_row_center')],
				'L{row}:P{row}'.format(row=n_row) : [x.name, self.formating_styles(workbook).get('table_row_left')],
				'Q{row}'.format(row=n_row) : [x.unit if x.unit else '', self.formating_styles(workbook).get('table_row_center')],
				'R{row}'.format(row=n_row) : [x.std if x.std else '', self.formating_styles(workbook).get('table_row_center')],
				'S{row}'.format(row=n_row) : [x.value if x.value else '', self.formating_styles(workbook).get('table_row_center')],
				'T{row}'.format(row=n_row) : [x.remark if x.remark else '', self.formating_styles(workbook).get('table_row_left')],
			}
		for key, value in cell_dict.items():
			key_split = key.split(':')
			if len(key_split) == 1:
				w_key = self.get_next_cell(key, n_row)
				worksheet.write(w_key, value[0], value[1])
			else:
				w_key = ':'.join(self.get_next_cell(k, n_row) for k in key_split)
				worksheet.merge_range(w_key, value[0], value[1])
			print(value)
		n_row +=1
		return n_row

	def generate_xlsx_report(self, workbook, data, objects):
		PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
		BASE_DIR = os.path.dirname(PROJECT_ROOT)
		PATH_DIR = '/static/src/img/'
		FILE_DIR = BASE_DIR + PATH_DIR
		FILE_NAME = 'logo.png'
		# print(objects)
		for obj in objects:
			print(obj.display_name)
			worksheet = workbook.add_worksheet("{} | {}".format(obj.name, obj.mo_id.number_ref))
			worksheet.set_column('A:A',3.8) # number
			worksheet.set_column('B:E',6.6) # name
			worksheet.set_column('F:F',9.7) # unit
			worksheet.set_column('G:H',6) # std
			worksheet.set_column('I:I',15.2) # value
			worksheet.set_column('J:J',18.2) # remarks

			worksheet.set_column('K:K',3.8)
			worksheet.set_column('L:O',6.6)
			worksheet.set_column('P:P',9.7)
			worksheet.set_column('Q:R',6)
			worksheet.set_column('S:S',15.2)
			worksheet.set_column('T:T',18.2)

			worksheet.merge_range('A2:D4', '', self.formating_styles(workbook).get('company_format'))
			worksheet.insert_image('A2:D4', FILE_DIR+FILE_NAME, {'x_scale': 1, 'y_scale': 1, 'x_offset':20})
			
			worksheet.merge_range('E2:R2', 'PRODUCTION DEPARTEMENT', self.formating_styles(workbook).get('company_format'))
			worksheet.merge_range('E3:R4', 'FORM MIXING ' + obj.product_id.name, self.formating_styles(workbook).get('company_format'))

			worksheet.write('S2', 'No Dok', self.formating_styles(workbook).get('table_left'))
			worksheet.write('S3', 'Tanggal', self.formating_styles(workbook).get('table_left'))
			worksheet.write('S4', 'Revisi: ', self.formating_styles(workbook).get('table_left'))
			worksheet.write('T2', ': ' + obj.name, self.formating_styles(workbook).get('table_left'))
			worksheet.write('T3', ': ' + obj.revision_date.strftime("%d-%m-%Y") if obj.revision_date else '', self.formating_styles(workbook).get('table_left'))
			worksheet.write('T4', ': ' + str(obj.revisi), self.formating_styles(workbook).get('table_left'))

			# Write Header of Report
			worksheet.merge_range('A5:D5', 'Hari / Tanggal', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('E5:J5', ': ' + obj.date.strftime("%d-%m-%Y") if obj.date else '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('A6:D6', 'Shift', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('E6:J6', ': ' + obj.shift if obj.shift else '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('K5:M5', 'Banded', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('N5:T5', ': ' + dict(obj._fields['banded'].selection).get(obj.banded) if obj.banded else '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('K6:M6', 'Batch', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('N6:T6', ': ' + obj.mo_id.number_ref if obj.mo_id else '', self.formating_styles(workbook).get('table_left'))

			worksheet.merge_range('A7:T7', 'PROCESS MIXING', self.formating_styles(workbook).get('table_header'))

			# Write Every Lines
			worksheet.write('A8', 'No.', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('B8:F8', 'Proses Produksi', self.formating_styles(workbook).get('page_title'))
			worksheet.write('G8', 'Unit', self.formating_styles(workbook).get('page_title'))
			worksheet.write('H8', 'Std', self.formating_styles(workbook).get('page_title'))
			worksheet.write('I8', 'Value', self.formating_styles(workbook).get('page_title'))
			worksheet.write('J8', 'Remark', self.formating_styles(workbook).get('page_title'))
			worksheet.write('K8', 'No.', self.formating_styles(workbook).get('page_title'))
			worksheet.merge_range('L8:P8', 'Proses Produksi', self.formating_styles(workbook).get('page_title'))
			worksheet.write('Q8', 'Unit', self.formating_styles(workbook).get('page_title'))
			worksheet.write('R8', 'Std', self.formating_styles(workbook).get('page_title'))
			worksheet.write('S8', 'Value', self.formating_styles(workbook).get('page_title'))
			worksheet.write('T8', 'Remark', self.formating_styles(workbook).get('page_title'))
			# row = 8
			# hdr = ['NO','PROSES PRODUKSI', 'UNIT']
			f_row = 9
			n_row = f_row
			lrow = 1
			reset = False
			m_row = len(obj.kmp_dumping_line) / 2 + obj.tolerance_precision
			# print(m_row)
			end_row = 0

			worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_1_title, self.formating_styles(workbook).get('page_title'))
			n_row +=1
			for x in obj.page_1_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1
				
			# print('POPPPPPPPPPPP ', obj.page_2_01_ids.pop())
			if obj.page_2_01_ids:
				if not reset:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_2_title, self.formating_styles(workbook).get('page_title'))
				else:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), obj.page_2_title, self.formating_styles(workbook).get('page_title'))
				n_row +=1
				lrow += 1

			for x in obj.page_2_01_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_02_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_02_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_03_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_03_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_04_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_04_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_05_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_05_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_06_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_06_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_07_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_07_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_08_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_08_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_09_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_09_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_10_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_10_ids:
				print('INI MASUK????')
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_2_11_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_2_11_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1

			if obj.page_3_01_ids:
				if not reset:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_3_title, self.formating_styles(workbook).get('page_title'))
				else:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), obj.page_3_title, self.formating_styles(workbook).get('page_title'))
				n_row +=1
				lrow += 1

			for x in obj.page_3_01_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_3_02_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_3_02_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_3_03_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_3_03_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1


			if obj.page_3_04_ids:
				if reset:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				else:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
				lrow += 1
				n_row +=1

			for x in obj.page_3_04_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1

			if obj.page_4_01_ids:
				if not reset:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_4_title, self.formating_styles(workbook).get('page_title'))
				else:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), obj.page_4_title, self.formating_styles(workbook).get('page_title'))
				n_row +=1
				lrow += 1

			for x in obj.page_4_01_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1

			


			if obj.page_5_01_ids:
				if not reset:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_5_title, self.formating_styles(workbook).get('page_title'))
				else:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), obj.page_5_title, self.formating_styles(workbook).get('page_title'))
				n_row +=1
				lrow += 1

			for x in obj.page_5_01_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1

			


			if obj.page_6_01_ids:
				if not reset:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_6_title, self.formating_styles(workbook).get('page_title'))
				else:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), obj.page_6_title, self.formating_styles(workbook).get('page_title'))
				n_row +=1
				lrow += 1

			for x in obj.page_6_01_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1

			


			if obj.page_7_01_ids:
				if not reset:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_7_title, self.formating_styles(workbook).get('page_title'))
				else:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), obj.page_7_title, self.formating_styles(workbook).get('page_title'))
				n_row +=1
				lrow += 1

			for x in obj.page_7_01_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1

			


			if obj.page_8_01_ids:
				if not reset:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_8_title, self.formating_styles(workbook).get('page_title'))
				else:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), obj.page_8_title, self.formating_styles(workbook).get('page_title'))
				n_row +=1
				lrow += 1

			for x in obj.page_8_01_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1

			


			if obj.page_qa_ids:
				if not reset:
					worksheet.merge_range('A{n_row}:J{n_row}'.format(n_row=n_row), obj.page_qa_title, self.formating_styles(workbook).get('page_title'))
				else:
					worksheet.merge_range('K{n_row}:T{n_row}'.format(n_row=n_row), obj.page_qa_title, self.formating_styles(workbook).get('page_title'))
				n_row +=1
				lrow += 1

			for x in obj.page_qa_ids:
				if lrow < m_row:
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					reset = True
					end_row = n_row - 1
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow +=1

			worksheet.merge_range('K{n_row}:T{end_row}'.format(n_row=n_row, end_row=end_row), '', self.formating_styles(workbook).get('space'))
			n_row = end_row + 1
			worksheet.merge_range('A{n_row}:M{end_row}'.format(n_row=n_row, end_row=n_row), 'Keterangan:', self.formating_styles(workbook).get('keterangan'))
			worksheet.merge_range('A{n_row}:M{end_row}'.format(n_row=n_row+1, end_row=n_row + 4), obj.ket, self.formating_styles(workbook).get('isi_keterangan'))
			worksheet.merge_range('N{n_row}:Q{end_row}'.format(n_row=n_row, end_row=n_row + 3), '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('R{n_row}:T{end_row}'.format(n_row=n_row, end_row=n_row + 3), '', self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('N{n_row}:Q{end_row}'.format(n_row=n_row+4, end_row=n_row + 4), 'Operator: {}'.format(obj.operator if obj.operator else ''), self.formating_styles(workbook).get('table_row_left'))
			worksheet.merge_range('R{n_row}:T{end_row}'.format(n_row=n_row+4, end_row=n_row + 4), 'Supervisor/Leader: {}'.format(obj.leader if obj.leader else '') , self.formating_styles(workbook).get('table_row_left'))