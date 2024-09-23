# -*- coding: utf-8 -*-

import io
from io import BytesIO
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
from odoo.tools import config

class LoaderXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_filling'
	_description = 'Daily Report Filling'
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
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['page_title'] = workbook.add_format(
			{'align': 'center', 'font_size': 10, 'border': 1, 'bold': True, 'font_name' : 'Times New Roman', })
		styles['space'] = workbook.add_format(
			{'border': 1,})
		styles['keterangan'] = workbook.add_format(
			{'align': 'left', 'valign':'top', 'border': 1, 'bold': True, 'bottom': 0, 'text_wrap':True, 'font_size': 10, 'font_name' : 'Times New Roman', })
		styles['isi_keterangan'] = workbook.add_format(
			{'align': 'left', 'valign':'top', 'border': 1, 'bold': True, 'top': 0, 'text_wrap':True, 'font_size': 10, 'font_name' : 'Times New Roman', })
		return styles

	def get_next_cell(self, cell, row):
		split_cell = re.split('(\d+)', cell)
		# next_row =  str(int(split_cell[1]) + row) 
		next_cell = split_cell[0] + str(row)
		return next_cell


	def write_dictionary(self, x, n_row, worksheet, workbook, reset=False):
		cell_dict = {}
		if x._name == 'kmi.filling.general.checks':
			cell_dict = {
				'A{row}:C{row}'.format(row=n_row) : [x.name, self.formating_styles(workbook).get('table_row_left')],
				'D{row}:E{row}'.format(row=n_row) : [x.standard if x.standard else '', self.formating_styles(workbook).get('table_row_center')],
				'F{row}:G{row}'.format(row=n_row) : [x.actual if x.actual else '', self.formating_styles(workbook).get('table_row_center')],
			}
			if reset:
				# print('SFGFDGHKFGJH')
				cell_dict = {
					'H{row}:J{row}'.format(row=n_row) : [x.name, self.formating_styles(workbook).get('table_row_left')],
					'K{row}:L{row}'.format(row=n_row) : [x.standard if x.standard else '', self.formating_styles(workbook).get('table_row_center')],
					'M{row}:N{row}'.format(row=n_row) : [x.actual if x.actual else '', self.formating_styles(workbook).get('table_row_center')],
				}
		elif x._name == 'kmi.filling.params.value':
			# print('PARAMS VALUEEEEEEEE')
			cell_dict = {
				'A{row}:B{row}'.format(row=n_row) : [x.name, self.formating_styles(workbook).get('table_row_left')],
				'C{row}'.format(row=n_row) : [x.param_1 if x.param_1 else '', self.formating_styles(workbook).get('table_row_center')],
				'D{row}'.format(row=n_row) : [x.param_2 if x.param_2 else '', self.formating_styles(workbook).get('table_row_center')],
				'E{row}'.format(row=n_row) : [x.param_3 if x.param_3 else '', self.formating_styles(workbook).get('table_row_center')],
				'F{row}'.format(row=n_row) : [x.param_4 if x.param_4 else '', self.formating_styles(workbook).get('table_row_center')],
				'G{row}'.format(row=n_row) : [x.param_5 if x.param_5 else '', self.formating_styles(workbook).get('table_row_center')],
				'H{row}'.format(row=n_row) : [x.param_6 if x.param_6 else '', self.formating_styles(workbook).get('table_row_center')],
			}
			if reset:
				# print('SFGFDGHKFGJH')
				cell_dict = {
					'K{row}:L{row}'.format(row=n_row) : [x.name, self.formating_styles(workbook).get('table_row_left')],
					'M{row}'.format(row=n_row) : [x.param_1 if x.param_1 else '', self.formating_styles(workbook).get('table_row_center')],
					'N{row}'.format(row=n_row) : [x.param_2 if x.param_2 else '', self.formating_styles(workbook).get('table_row_center')],
					'O{row}'.format(row=n_row) : [x.param_3 if x.param_3 else '', self.formating_styles(workbook).get('table_row_center')],
					'P{row}'.format(row=n_row) : [x.param_4 if x.param_4 else '', self.formating_styles(workbook).get('table_row_center')],
					'Q{row}'.format(row=n_row) : [x.param_5 if x.param_5 else '', self.formating_styles(workbook).get('table_row_center')],
					'R{row}'.format(row=n_row) : [x.param_6 if x.param_6 else '', self.formating_styles(workbook).get('table_row_center')],
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
			worksheet.set_column('A:A', 7)
			worksheet.set_column('B:B', 7)
			worksheet.set_column('C:C', 7)
			worksheet.set_column('D:D', 7)
			worksheet.set_column('E:E', 7)
			worksheet.set_column('F:F', 7)
			worksheet.set_column('G:G', 7)
			worksheet.set_column('H:H', 7)
			worksheet.set_column('I:I', 7)
			worksheet.set_column('J:J', 7)
			worksheet.set_column('K:K', 7)
			worksheet.set_column('L:L', 7)
			worksheet.set_column('M:M', 7)
			worksheet.set_column('N:N', 7)

			worksheet.merge_range('A2:D5', '', self.formating_styles(workbook).get('company_format'))
			worksheet.insert_image('A2:D5', FILE_DIR+FILE_NAME, {'x_scale': 1.5, 'y_scale': 1.5, 'x_offset':15})
			
			worksheet.merge_range('E2:R3', 'PRODUCTION DEPARTMENT', self.formating_styles(workbook).get('company_format'))
			worksheet.merge_range('E4:R5', 'Form Laporan Harian Filling (OBOL)', self.formating_styles(workbook).get('company_format'))

			worksheet.write('S2', 'No Dok', self.formating_styles(workbook).get('table_left'))
			worksheet.write('S3', 'Tanggal', self.formating_styles(workbook).get('table_left'))
			worksheet.write('S4', 'Hal', self.formating_styles(workbook).get('table_left'))
			worksheet.write('S5', 'Revisi', self.formating_styles(workbook).get('table_left'))

			worksheet.merge_range('T2:U2', ': {}'.format(obj.name), self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('T3:U3', ': {}'.format(obj.release_date.strftime("%d-%m-%Y")), self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('T4:U4', ': ', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('T5:U5', ': {}'.format(obj.revision), self.formating_styles(workbook).get('table_left'))

			worksheet.merge_range('A6:U6', '', self.formating_styles(workbook).get('space'))
# =========================================================================================        

			worksheet.merge_range('R7:U7', 'Production Notes', self.formating_styles(workbook).get('company_format'))
			worksheet.merge_range('R8:S8', 'Hari', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('R9:S9', 'Tanggal', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('R10:S10', 'Shift', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('R11:S11', 'Team', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('R12:S12', 'Kemasan (ml)', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('R13:S13', 'Line Machine', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('R14:U14', '', self.formating_styles(workbook).get('company_format'))

			worksheet.merge_range('T8:U8', dict(obj._fields['dayofweek'].selection).get(obj.dayofweek), self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('T9:U9', str(obj.date), self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('T10:U10', obj.shift, self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('T11:U11', obj.team, self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('T12:U12', obj.packaging, self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('T13:U13', obj.line_machine, self.formating_styles(workbook).get('table_center'))			    

			worksheet.merge_range('A7:Q7', 'GENERAL REPORT', self.formating_styles(workbook).get('company_format'))
			worksheet.merge_range('A8:C8', 'Preparation', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('A9:C9', 'Total Breakdown', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('A10:C10', 'Running hours', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('A11:C11', 'Total output / shift', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('A12:C12', 'Total output / running hours', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('A13:C13', 'Total Reject', self.formating_styles(workbook).get('table_left'))

			worksheet.merge_range('D8:E8', obj.preparation, self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D9:E9', obj.total_breakdown, self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D10:E10', obj.running_hours, self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D11:E11', obj.total_output_shift or '', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D12:E12', obj.total_output_hours or '', self.formating_styles(workbook).get('table_center'))
			worksheet.merge_range('D13:E13', obj.total_reject_produk or '', self.formating_styles(workbook).get('table_center'))

			worksheet.write('F8', 'min', self.formating_styles(workbook).get('table_center'))
			worksheet.write('F9', 'min', self.formating_styles(workbook).get('table_center'))
			worksheet.write('F10', 'min', self.formating_styles(workbook).get('table_center'))
			worksheet.write('F11', 'btl', self.formating_styles(workbook).get('table_center'))
			worksheet.write('F12', 'btl/min', self.formating_styles(workbook).get('table_center'))

			worksheet.merge_range('G8:I8', 'No BO / Batch ', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('G9:I9', 'Start Loading Actual', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('G10:I10', 'Finish Loading Actual ', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('G11:I11', 'Output/batch (btl) ', self.formating_styles(workbook).get('table_left'))
			# worksheet.merge_range('G12:I12', 'Reject/batch (btl) ', self.formating_styles(workbook).get('table_left'))
			worksheet.merge_range('G12:I12', 'Reject/batch (btl)  ', self.formating_styles(workbook).get('table_left'))
			c = 9
			general_line = [k for k in obj.batch_line]
			for i in general_line:
				sa = '%02d:%02d' % (int(i.start_coding), i.start_coding % 1 * 60)
				fa = '%02d:%02d' % (int(i.end_coding), i.end_coding % 1 * 60)
				worksheet.write(7, c, i.batch_number, self.formating_styles(workbook).get('table_center'))
				worksheet.write(8, c, sa, self.formating_styles(workbook).get('table_center'))
				worksheet.write(9, c, fa, self.formating_styles(workbook).get('table_center'))
				worksheet.write(10, c, i.output_batch or '', self.formating_styles(workbook).get('table_center'))
				worksheet.write(11, c, i.reject_batch or '', self.formating_styles(workbook).get('table_center'))
				c += 1
			# worksheet.merge_range('A14:U14', 'Notes', self.formating_styles(workbook).get('table_center'))
			# worksheet.merge_range('A15:U16', obj.note or '', self.formating_styles(workbook).get('company_format'))
# =========================================================================================       

			# VERIFIKASI CODING BODY
			n_row = 14
			worksheet.merge_range('A{row}:U{row}'.format(row=n_row), 'VERIFIKASI CODING BODI (setiap batch)', self.formating_styles(workbook).get('company_format'))
			n_row += 1
			merge_row = n_row + 1 # Row yang digunakan untuk row sub header / merge n_row dan row selanjutnya
			worksheet.merge_range('A{row}:C{merge_row}'.format(row=n_row, merge_row=merge_row), 'Setting Coding Bodi Botol (oleh QC)', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('D{row}:H{merge_row}'.format(row=n_row, merge_row=merge_row), 'Actual Coding Bodi Botol (upload)', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('I{row}:L{row}'.format(row=n_row), 'Cetak Coding oleh Produksi', self.formating_styles(workbook).get('table_row_center'))
			# Turunan 'Cetak Coding oleh Produksi'
			worksheet.merge_range('I{row}:J{row}'.format(row=merge_row), 'PIC', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('K{row}:L{row}'.format(row=merge_row), 'Jam cetak coding', self.formating_styles(workbook).get('table_row_center'))

			worksheet.merge_range('M{row}:R{row}'.format(row=n_row), 'Verifikasi Coding oleh QC', self.formating_styles(workbook).get('table_row_center'))
			# Turunan 'Verifikasi Coding Oleh QC'
			worksheet.merge_range('M{row}:N{row}'.format(row=merge_row), 'PIC', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('O{row}:P{row}'.format(row=merge_row), 'Jam cetak coding', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('Q{row}:R{row}'.format(row=merge_row), 'Status', self.formating_styles(workbook).get('table_row_center'))

			worksheet.merge_range('S{row}:U{row}'.format(row=n_row), 'Notes', self.formating_styles(workbook).get('table_row_center'))
			# worksheet.write('R{row}'.format(row=n_row), 'Actual', self.formating_styles(workbook).get('table_row_center'))
			# worksheet.merge_range('S{row}:U{row}'.format(row=n_row), 'Notes :', self.formating_styles(workbook).get('table_row_center'))
			n_row = merge_row + 1

			filestore_path = config.filestore(self._cr.dbname)
			# print(filestore_path)
			# filelocation = self.env['ir.attachment'].search([('name','=', 'actual_coding')])

			for x in obj.verify_coding_line:
				print(n_row)
				worksheet.set_row(n_row-1, 100)
				worksheet.merge_range('A{row}:C{row}'.format(row=n_row), x.set_coding_by_qc if x.set_coding_by_qc else '', self.formating_styles(workbook).get('table_row_center'))
				self._cr.execute("""SELECT store_fname FROM ir_attachment WHERE res_model = '{}' AND res_id = {}""".format(x._name,x.id))
				fetch = self._cr.dictfetchone()
				img_file = open(filestore_path + "/" + fetch['store_fname'], 'rb')
				file_data = io.BytesIO(img_file.read())
				img_file.close()
				worksheet.merge_range('D{row}:H{row}'.format(row=n_row), '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.insert_image('D{row}:H{row}'.format(row=n_row), 'file_data.jpeg', {'image_data': file_data,'x_scale': 0.5, 'y_scale': 0.5, 'x_offset':100})
				worksheet.merge_range('I{row}:J{row}'.format(row=n_row), x.pic_produksi if x.pic_produksi else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('K{row}:L{row}'.format(row=n_row), self._convert_to_time(x.jam_cetak_coding) if x.jam_cetak_coding else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('M{row}:N{row}'.format(row=n_row), x.pic_qc if x.pic_qc else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('O{row}:P{row}'.format(row=n_row), self._convert_to_time(x.jam_verifikasi_coding) if x.jam_verifikasi_coding else '', self.formating_styles(workbook).get('table_row_center'))
				worksheet.merge_range('Q{row}:R{row}'.format(row=n_row), x.status_verifikasi if x.status_verifikasi else '', self.formating_styles(workbook).get('table_row_center'))
				n_row += 1

			worksheet.merge_range('S{merge_row}:U{row}'.format(row=n_row,merge_row=merge_row), '', self.formating_styles(workbook).get('table_row_center'))

			# PERSIAPAN AWAL PENCETAKAN GENERAL CHECKS
			worksheet.merge_range('A{row}:U{row}'.format(row=n_row), 'GENERAL CHECKS ( early shift checks)', self.formating_styles(workbook).get('company_format'))
			n_row += 1
			worksheet.merge_range('A{row}:C{row}'.format(row=n_row), 'Parameter', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('D{row}:E{row}'.format(row=n_row), 'Std', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('F{row}:G{row}'.format(row=n_row), 'Actual', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('H{row}:J{row}'.format(row=n_row), 'Parameter', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('K{row}:L{row}'.format(row=n_row), 'Std', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('M{row}:N{row}'.format(row=n_row), 'Actual', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('O{row}:P{row}'.format(row=n_row), 'Parameter', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('Q{row}'.format(row=n_row), 'Std', self.formating_styles(workbook).get('table_row_center'))
			worksheet.write('R{row}'.format(row=n_row), 'Actual', self.formating_styles(workbook).get('table_row_center'))
			worksheet.merge_range('S{row}:U{row}'.format(row=n_row), 'Notes :', self.formating_styles(workbook).get('table_row_center'))
			n_row += 1

			f_row = n_row # First Row untuk sebagai acuan row ketika reset general checks
			# n_row = 21 # row yang digunakan untuk looping pertama general checks
			lrow = 1
			reset = False
			total_row_gen_checks = len(obj.checks_line)
			m_row = total_row_gen_checks / 2 
			# print(m_row)
			end_row = 0
			# print('############### ',total_row_gen_checks)
			for x in obj.checks_line:
				if lrow <= m_row:
					print('===atas=====',n_row)
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
				else:
					print('===bawah=====')
					reset = True
					end_row = n_row
					n_row = f_row
					n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
					lrow = 1
				lrow += 1

			# n_row = f_row
			# worksheet.merge_range('O{row}:R{row}'.format(row=n_row), 'Current Step Loading', self.formating_styles(workbook).get('table_row_center'))
			# n_row += 1
			# # Cetak Data Current Step Loading
			# worksheet.merge_range('O{row}:P{row}'.format(row=n_row), 'Running Production', self.formating_styles(workbook).get('table_row_center'))
			# worksheet.merge_range('Q{row}:R{row}'.format(row=n_row), obj.run_production, self.formating_styles(workbook).get('table_row_center'))
			# n_row += 1
			# worksheet.merge_range('O{row}:P{row}'.format(row=n_row), 'Preparation(CLS)', self.formating_styles(workbook).get('table_row_center'))
			# worksheet.merge_range('Q{row}:R{row}'.format(row=n_row), obj.preparation_cls, self.formating_styles(workbook).get('table_row_center'))
			# n_row += 1
			# worksheet.merge_range('O{row}:P{row}'.format(row=n_row), 'Shuttle Car', self.formating_styles(workbook).get('table_row_center'))
			# worksheet.merge_range('Q{row}:R{row}'.format(row=n_row), obj.shuttle_car, self.formating_styles(workbook).get('table_row_center'))
			# n_row += 1
			# worksheet.merge_range('O{row}:P{row}'.format(row=n_row), 'Other', self.formating_styles(workbook).get('table_row_center'))
			# worksheet.merge_range('Q{row}:R{row}'.format(row=n_row), obj.other, self.formating_styles(workbook).get('table_row_center'))
			# n_row += 1
			# worksheet.merge_range('O{row}:R{row}'.format(row=n_row), '', self.formating_styles(workbook).get('space'))

			# n_row = f_row
			# lrow = n_row + 5
			# worksheet.merge_range('S{frow}:U{lrow}'.format(frow=n_row,lrow=lrow), obj.note_checks, self.formating_styles(workbook).get('table_row_center'))
			# n_row = lrow

			# # PRODUCTION RECORDS BARIS PERTAMA
			# worksheet.merge_range('A{row}:U{row}'.format(row=n_row), 'PRODUCTION RECORDS', self.formating_styles(workbook).get('company_format'))

			# title_row = n_row
			# f_row = n_row + 1
			# n_row = f_row
			# reset = True # Jika Bernilai False --> Seharusnya berada di sebelah kiri, Jika Bernilai True Maka berada di sebelah kanan
			# # lrow = 1
			# if obj.batch_1:
			# 	f_row = n_row
			# 	n_row = f_row
			# 	reset = True if reset == False else False # reset menjadi True ketika reset sebelumnya bernilai False, begitu juga sebaliknya
			# 	title_row = n_row if reset == False else title_row
			# 	if not reset:
			# 		worksheet.merge_range('A{row}:B{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('C{row}:H{row}'.format(row=title_row), obj.batch_1, self.formating_styles(workbook).get('table_row_center'))
			# 	else:
			# 		n_row = f_row
			# 		worksheet.merge_range('K{row}:L{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('M{row}:R{row}'.format(row=title_row), obj.batch_1, self.formating_styles(workbook).get('table_row_center'))

			# 	n_row += 1
			# 	print(reset)
			# 	for x in obj.prod_rec_1_line:
			# 		n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)
			# 	print(n_row) # Harus nya 35

			# 	# CETAK NOTES
			# 	if reset:
			# 		worksheet.merge_range('S{row}:U{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('table_row_left'))
			# 		worksheet.merge_range('S{title_row}:U{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_1 if obj.batch_note_1 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	else:
			# 		worksheet.merge_range('I{row}:J{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('I{title_row}:J{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_1 if obj.batch_note_1 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	worksheet.merge_range('A{n_row}:U{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			# 	n_row = n_row + 1

			# if obj.batch_2:
			# 	# f_row = n_row
			# 	n_row = f_row
			# 	reset = True if reset == False else False # reset menjadi True ketika reset sebelumnya bernilai False, begitu juga sebaliknya
			# 	title_row = n_row if reset == False else title_row
			# 	if not reset:
			# 		worksheet.merge_range('A{row}:B{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('C{row}:H{row}'.format(row=title_row), obj.batch_2, self.formating_styles(workbook).get('table_row_center'))
			# 	else:
			# 		n_row = f_row
			# 		worksheet.merge_range('K{row}:L{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('M{row}:R{row}'.format(row=title_row), obj.batch_2, self.formating_styles(workbook).get('table_row_center'))

			# 	n_row += 1
			# 	print(reset)
			# 	# print(n_row)
			# 	for x in obj.prod_rec_2_line:
			# 		n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)

			# 	# CETAK NOTES
			# 	if reset:
			# 		worksheet.merge_range('S{row}:U{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('S{title_row}:U{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_2 if obj.batch_note_2 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	else:
			# 		worksheet.merge_range('I{row}:J{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('I{title_row}:J{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_2 if obj.batch_note_2 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	worksheet.merge_range('A{n_row}:U{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			# 	n_row = n_row + 1

			# if obj.batch_3:
			# 	f_row = n_row
			# 	n_row = f_row
			# 	reset = True if reset == False else False # reset menjadi True ketika reset sebelumnya bernilai False, begitu juga sebaliknya
			# 	title_row = n_row if reset == False else title_row
			# 	if not reset:
			# 		worksheet.merge_range('A{row}:B{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('C{row}:H{row}'.format(row=title_row), obj.batch_3, self.formating_styles(workbook).get('table_row_center'))
			# 	else:
			# 		n_row = f_row
			# 		worksheet.merge_range('K{row}:L{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('M{row}:R{row}'.format(row=title_row), obj.batch_3, self.formating_styles(workbook).get('table_row_center'))

			# 	n_row += 1
			# 	for x in obj.prod_rec_3_line:
			# 		n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)

			# 	# CETAK NOTES
			# 	if reset:
			# 		worksheet.merge_range('S{row}:U{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('table_row_left'))
			# 		worksheet.merge_range('S{title_row}:U{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_3 if obj.batch_note_3 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	else:
			# 		worksheet.merge_range('I{row}:J{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('I{title_row}:J{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_3 if obj.batch_note_3 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	worksheet.merge_range('A{n_row}:U{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			# 	n_row = n_row + 1

			# if obj.batch_4:
			# 	f_row = n_row
			# 	n_row = f_row
			# 	reset = True if reset == False else False # reset menjadi True ketika reset sebelumnya bernilai False, begitu juga sebaliknya
			# 	title_row = n_row if reset == False else title_row
			# 	if not reset:
			# 		worksheet.merge_range('A{row}:B{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('C{row}:H{row}'.format(row=title_row), obj.batch_4, self.formating_styles(workbook).get('table_row_center'))
			# 	else:
			# 		worksheet.merge_range('K{row}:L{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('M{row}:R{row}'.format(row=title_row), obj.batch_4, self.formating_styles(workbook).get('table_row_center'))
			# 		n_row = title_row

			# 	# print(reset)
			# 	n_row += 1
			# 	for x in obj.prod_rec_4_line:
			# 		# print(n_row)
			# 		n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)

			# 	# CETAK NOTES
			# 	if reset:
			# 		worksheet.merge_range('S{row}:U{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('S{title_row}:U{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_4 if obj.batch_note_4 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	else:
			# 		worksheet.merge_range('I{row}:J{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('I{title_row}:J{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_4 if obj.batch_note_4 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	worksheet.merge_range('A{n_row}:U{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			# 	n_row = n_row + 1

			# if obj.batch_5:
			# 	f_row = n_row
			# 	n_row = f_row
			# 	reset = True if reset == False else False # reset menjadi True ketika reset sebelumnya bernilai False, begitu juga sebaliknya
			# 	title_row = n_row if reset == False else title_row
			# 	if not reset:
			# 		worksheet.merge_range('A{row}:B{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('C{row}:H{row}'.format(row=title_row), obj.batch_5, self.formating_styles(workbook).get('table_row_center'))
			# 	else:
			# 		worksheet.merge_range('K{row}:L{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('M{row}:R{row}'.format(row=title_row), obj.batch_5, self.formating_styles(workbook).get('table_row_center'))
			# 		n_row = title_row

			# 	n_row += 1
			# 	for x in obj.prod_rec_5_line:
			# 		n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)

			# 	# CETAK NOTES
			# 	if reset:
			# 		worksheet.merge_range('S{row}:U{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('S{title_row}:U{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_5 if obj.batch_note_5 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	else:
			# 		worksheet.merge_range('I{row}:J{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('I{title_row}:J{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_5 if obj.batch_note_5 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	worksheet.merge_range('A{n_row}:U{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			# 	n_row = n_row + 1

			# if obj.batch_6:
			# 	f_row = n_row
			# 	n_row = f_row
			# 	reset = True if reset == False else False # reset menjadi True ketika reset sebelumnya bernilai False, begitu juga sebaliknya
			# 	title_row = n_row if reset == False else title_row
			# 	if not reset:
			# 		worksheet.merge_range('A{row}:B{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('C{row}:H{row}'.format(row=title_row), obj.batch_6, self.formating_styles(workbook).get('table_row_center'))
			# 	else:
			# 		worksheet.merge_range('K{row}:L{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('M{row}:R{row}'.format(row=title_row), obj.batch_6, self.formating_styles(workbook).get('table_row_center'))
			# 		n_row = title_row

			# 	n_row += 1
			# 	for x in obj.prod_rec_6_line:
			# 		n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)

			# 	# CETAK NOTES
			# 	if reset:
			# 		worksheet.merge_range('S{row}:U{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('S{title_row}:U{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_6 if obj.batch_note_6 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	else:
			# 		worksheet.merge_range('I{row}:J{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('I{title_row}:J{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_6 if obj.batch_note_6 else '', self.formating_styles(workbook).get('isi_keterangan'))

			# 	worksheet.merge_range('A{n_row}:U{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			# 	n_row = n_row + 1

			# if obj.batch_7:
			# 	f_row = n_row
			# 	n_row = f_row
			# 	reset = True if reset == False else False # reset menjadi True ketika reset sebelumnya bernilai False, begitu juga sebaliknya
			# 	title_row = n_row if reset == False else title_row
			# 	if not reset:
			# 		worksheet.merge_range('A{row}:B{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('C{row}:H{row}'.format(row=title_row), obj.batch_7, self.formating_styles(workbook).get('table_row_center'))
			# 	else:
			# 		worksheet.merge_range('K{row}:L{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('M{row}:R{row}'.format(row=title_row), obj.batch_7, self.formating_styles(workbook).get('table_row_center'))
			# 		n_row = title_row

			# 	n_row += 1
			# 	for x in obj.prod_rec_7_line:
			# 		n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)

			# 	# CETAK NOTES
			# 	if reset:
			# 		worksheet.merge_range('S{row}:U{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('S{title_row}:U{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_7 if obj.batch_note_7 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	else:
			# 		worksheet.merge_range('I{row}:J{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('I{title_row}:J{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_7 if obj.batch_note_7 else '', self.formating_styles(workbook).get('isi_keterangan'))

			# 	worksheet.merge_range('A{n_row}:U{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			# 	n_row = n_row + 1

			# if obj.batch_8:
			# 	f_row = n_row
			# 	n_row = f_row
			# 	reset = True if reset == False else False # reset menjadi True ketika reset sebelumnya bernilai False, begitu juga sebaliknya
			# 	title_row = n_row if reset == False else title_row
			# 	if not reset:
			# 		worksheet.merge_range('A{row}:B{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('C{row}:H{row}'.format(row=title_row), obj.batch_8, self.formating_styles(workbook).get('table_row_center'))
			# 	else:
			# 		worksheet.merge_range('K{row}:L{row}'.format(row=title_row), 'No BO / Batch', self.formating_styles(workbook).get('table_row_center'))
			# 		worksheet.merge_range('M{row}:R{row}'.format(row=title_row), obj.batch_8, self.formating_styles(workbook).get('table_row_center'))
			# 		n_row = title_row

			# 	n_row += 1
			# 	for x in obj.prod_rec_8_line:
			# 		n_row = self.write_dictionary(x, n_row, worksheet, workbook, reset=reset)

			# 	# CETAK NOTES
			# 	if reset:
			# 		worksheet.merge_range('S{row}:U{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('S{title_row}:U{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_8 if obj.batch_note_8 else '', self.formating_styles(workbook).get('isi_keterangan'))
			# 	else:
			# 		worksheet.merge_range('I{row}:J{row}'.format(row=title_row), 'Notes:', self.formating_styles(workbook).get('keterangan'))
			# 		worksheet.merge_range('I{title_row}:J{n_row}'.format(title_row=title_row +1, n_row=n_row-1), obj.batch_note_8 if obj.batch_note_8 else '', self.formating_styles(workbook).get('isi_keterangan'))

			# 	worksheet.merge_range('A{n_row}:U{n_row}'.format(n_row=n_row), '', self.formating_styles(workbook).get('space'))
			# 	n_row = n_row + 1

			# if reset == False:
			# 	worksheet.merge_range('K{f_row}:U{n_row}'.format(f_row=f_row,n_row=n_row-2), '', self.formating_styles(workbook).get('space'))
			# worksheet.merge_range('A{row}:C{row2}'.format(row=n_row, row2=n_row+3), 'IMPORTANT NOTES', self.formating_styles(workbook).get('keterangan'))
			# worksheet.merge_range('D{row}:U{row2}'.format(row=n_row, row2=n_row+3), 
			# 	"""*Pencatatan start/finish jam per keranjang mengacu jam coding pada produk\nJam start =  botol terdepan pada layer paling bawah\nJam finish = botol terakhir pada layer paling atas""", self.formating_styles(workbook).get('isi_keterangan'))
			# n_row += 4


			# worksheet.merge_range('A{row}:U{row}'.format(row=n_row), 'CATATAN KETIDAKSESUAIAN SELAMA PROSES PRODUKSI', self.formating_styles(workbook).get('company_format'))
			# n_row += 1
			# worksheet.merge_range('A{row}:U{row}'.format(row=n_row), 'Breakdown', self.formating_styles(workbook).get('company_format'))
			# n_row += 1
			# worksheet.write('A{n_row}'.format(n_row=n_row), 'No', self.formating_styles(workbook).get('page_title'))
			# worksheet.write('B{n_row}'.format(n_row=n_row), 'Start', self.formating_styles(workbook).get('page_title'))
			# worksheet.write('C{n_row}'.format(n_row=n_row), 'Finish', self.formating_styles(workbook).get('page_title'))
			# worksheet.write('D{n_row}'.format(n_row=n_row), 'Total', self.formating_styles(workbook).get('page_title'))
			# worksheet.merge_range('E{row}:O{row}'.format(row=n_row), 'Uraian Masalah', self.formating_styles(workbook).get('page_title'))
			# worksheet.merge_range('P{row}:Q{row}'.format(row=n_row), 'Frekuensi', self.formating_styles(workbook).get('page_title'))
			# worksheet.merge_range('R{row}:S{row}'.format(row=n_row), 'Status', self.formating_styles(workbook).get('page_title'))
			# worksheet.merge_range('T{row}:U{row}'.format(row=n_row), 'PIC', self.formating_styles(workbook).get('page_title'))
			# n_row += 1
			# no = 1
			# for x in obj.incompatibility_line:
			# 	worksheet.write('A{n_row}'.format(n_row=n_row), no, self.formating_styles(workbook).get('table_row_center'))
			# 	worksheet.write('B{n_row}'.format(n_row=n_row), self._convert_to_time(round(float(x.start),15)), self.formating_styles(workbook).get('table_row_center'))
			# 	worksheet.write('C{n_row}'.format(n_row=n_row), self._convert_to_time(round(float(x.finish),15)), self.formating_styles(workbook).get('table_row_center'))
			# 	worksheet.write('D{n_row}'.format(n_row=n_row), self._convert_to_time(round(float(x.total),15)), self.formating_styles(workbook).get('table_row_center'))
			# 	worksheet.merge_range('E{row}:O{row}'.format(row=n_row), x.uraian_masalah, self.formating_styles(workbook).get('table_row_center'))
			# 	worksheet.merge_range('P{row}:Q{row}'.format(row=n_row), x.frekuensi, self.formating_styles(workbook).get('table_row_center'))
			# 	worksheet.merge_range('R{row}:S{row}'.format(row=n_row), x.status, self.formating_styles(workbook).get('table_row_center'))
			# 	worksheet.merge_range('T{row}:U{row}'.format(row=n_row), x.pic, self.formating_styles(workbook).get('table_row_center'))
			# 	no += 1
			# 	n_row += 1

			# worksheet.merge_range('A{frow}:M{lrow}'.format(frow=n_row,lrow=n_row+4), 'Another awesome notes:\n{awesome_note}'.format(awesome_note=obj.another_note), self.formating_styles(workbook).get('isi_keterangan'))
			# worksheet.merge_range('N{frow}:Q{lrow}'.format(frow=n_row,lrow=n_row+3), '', self.formating_styles(workbook).get('space'))
			# worksheet.merge_range('R{frow}:U{lrow}'.format(frow=n_row,lrow=n_row+3), '', self.formating_styles(workbook).get('space'))
			# n_row += 4
			# worksheet.merge_range('N{frow}:Q{lrow}'.format(frow=n_row,lrow=n_row), 'Operator: {}'.format(obj.operator), self.formating_styles(workbook).get('table_row_center'))
			# worksheet.merge_range('R{frow}:U{lrow}'.format(frow=n_row,lrow=n_row), 'Leader / Supervisor: {}'.format(obj.leader), self.formating_styles(workbook).get('table_row_center'))
			
