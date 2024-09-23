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


class PartnerXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_unscramble'
	_description = 'Daily Report Unscramble'
	_inherit = 'report.report_xlsx.abstract'

	def generate_xlsx_report(self, workbook, data, partners):
		PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
		BASE_DIR = os.path.dirname(PROJECT_ROOT)
		PATH_DIR = '/static/src/img/'
		FILE_DIR = BASE_DIR + PATH_DIR
		FILE_NAME = 'logo.png'

		for obj in partners:
			company_format = workbook.add_format(
				{'align': 'center', 'valign':'vcenter','font_color': 'black', 'border': 1, 'bold': True})
			table_header = workbook.add_format(
				{'align': 'center', 'font_size': 12,'font_color': 'black', 'border': 1, 'bold': True})

			table_row_left = workbook.add_format(
				{'align': 'left', 'font_size': 12, 'border': 1})
			table_row_right = workbook.add_format(
				{'align': 'center', 'font_size': 12, 'border': 1, 'bold': True})
			table_left = workbook.add_format(
				{'align': 'left', 'border': 1, 'bold': True})
			table_center = workbook.add_format(
				{'align': 'center', 'border': 1, 'bold': True})

			worksheet = workbook.add_worksheet(obj.name)

			# set col width
			worksheet.set_column('A:A', 13)
			worksheet.set_column('B:B', 10)
			worksheet.set_column('C:C', 10)
			worksheet.set_column('D:D', 10)
			worksheet.set_column('E:E', 10)
			worksheet.set_column('F:F', 10)
			worksheet.set_column('G:G', 10)
			worksheet.set_column('H:H', 10)
			worksheet.set_column('I:I', 10)
			worksheet.set_column('J:J', 10)
			worksheet.set_column('K:K', 10)
			worksheet.set_column('L:L', 10)
			worksheet.set_column('M:M', 10)
			worksheet.set_column('N:N', 10)

			worksheet.merge_range('A2:D5', '', company_format)
			worksheet.insert_image('A2:D5', FILE_DIR+FILE_NAME, {'x_scale': 1.5, 'y_scale': 1.5, 'x_offset':20})
			
			worksheet.merge_range('E2:R3', 'PRODUCTION DEPARTMENT', company_format)
			worksheet.merge_range('E4:R5', 'Form Laporan Harian Unscramble Machine ', company_format)

			conf_module = self.env['kmi.unscramble'].search([('state', 'in', ['draft_model', 'model'])], limit=1)
			worksheet.merge_range('S2:U2', 'No Dok: ' + obj.name, table_left)
			worksheet.merge_range('S3:U3', 'Tanggal: ' + str(conf_module.release_date.strftime("%d-%m-%Y")), table_left)
			worksheet.merge_range('S4:U4', 'Hal: ', table_left)
			worksheet.merge_range('S5:U5', 'Revisi: '+ str(obj.revision), table_left)

			worksheet.merge_range('A7:P7', 'GENERAL REPORT', company_format)
			worksheet.merge_range('Q7:U7', 'Notes', company_format)
			# KIRI
			worksheet.write('A8', 'OKP', table_left)
			worksheet.write('A9', 'Bottle Silo', table_left)
			worksheet.write('A10', 'No Urut BO', table_left)
			worksheet.write('A11', 'Hari', table_left)
			worksheet.write('A12', 'Tanggal', table_left)
			worksheet.write('A13', 'Shift', table_left)

			data = dict(obj.fields_get(['dayofweek'])['dayofweek']['selection'])
			day = [v for k,v in data.items() if k == obj.dayofweek ][0]
			worksheet.write('B8', obj.okp_id.name, table_center)
			worksheet.write('B9', obj.product_silo_id.display_name, table_center)
			worksheet.write('B10', obj.no_urut_bo, table_center)
			worksheet.write('B11', day, table_center)
			worksheet.write('B12', str(obj.date.strftime("%d-%m-%Y")), table_center)
			worksheet.write('B13', obj.shift, table_center)

			worksheet.write('C8', 'Operator', table_left)
			worksheet.write('C9', 'Leader', table_left)
			worksheet.write('C10', 'Team', table_left)
			worksheet.write('C11', 'Kemasan (ml)', table_left)
			worksheet.write('C12', 'Line Machine', table_left)

			worksheet.write('D8', obj.operator, table_center)
			worksheet.write('D9', obj.leader, table_center)
			worksheet.write('D10', obj.team, table_center)
			worksheet.write('D11', obj.packaging, table_center)
			worksheet.write('D12', obj.line_machine, table_center)
			# KANAN
			worksheet.merge_range('F8:H8', 'Preparation', table_left)
			worksheet.merge_range('F9:H9', 'Total Breakdown', table_left)
			worksheet.merge_range('F10:H10', 'Running hours', table_left)
			worksheet.merge_range('F11:H11', 'Total reject unscramble A', table_left)
			worksheet.merge_range('F12:H12', 'Total reject unscramble B', table_left)
			worksheet.merge_range('F13:H13', 'Total reject Rinser', table_left)
			worksheet.merge_range('F14:H14', 'Speed max unscramble A', table_left)
			worksheet.merge_range('F15:H15', 'Speed max unscramble B', table_left)

			worksheet.write('I8', obj.preparation, table_center)
			worksheet.write('I9', obj.total_breakdown, table_center)
			worksheet.write('I10', obj.running_hours, table_center)
			worksheet.write('I11', obj.total_reject_unscramble_a, table_center)
			worksheet.write('I12', obj.total_reject_unscramble_b, table_center)
			worksheet.write('I13', obj.total_reject_rinser, table_center)
			worksheet.write('I14', obj.speed_max_unscramble_a, table_center)
			worksheet.write('I15', obj.speed_max_unscramble_b, table_center)

			worksheet.write('J8', 'min', table_center)
			worksheet.write('J9', 'min', table_center)
			worksheet.write('J10', 'min', table_center)
			worksheet.write('J11', 'btl', table_center)
			worksheet.write('J12', 'btl', table_center)
			worksheet.write('J13', 'btl', table_center)
			worksheet.write('J14', 'btl/min', table_center)
			worksheet.write('J15', 'btl/min', table_center)

			worksheet.merge_range('K8:L8', 'NO. BO ', table_left)
			worksheet.merge_range('K9:L9', 'Product Name', table_left)
			worksheet.merge_range('K10:L10', 'Start Production Time', table_left)
			worksheet.merge_range('K11:L11', 'Counter Rinser ', table_left)
			c = 12
			general_line = [k for k in obj.batch_line]
			for i in general_line:
				start_time = '%02d:%02d' % (int(i.start_coding), i.start_coding % 1 * 60) or ''
				worksheet.write(7, c, i.batch_number, table_center)
				worksheet.write(8, c, i.product_id.display_name, table_center)
				worksheet.write(9, c, start_time, table_center)
				worksheet.write(10, c, i.end_coding, table_center)
				c += 1

			# NOTES
			worksheet.merge_range('Q8:U15', '', company_format)
			
			worksheet.merge_range('A17:G17', 'GENERAL CHECKS ( early shift checks)', company_format)
			
			worksheet.merge_range('A18:C18', 'Parameter', table_header)
			worksheet.merge_range('D18:E18', 'Std', table_header)
			worksheet.merge_range('F18:G18', 'Actual', table_header)

			check = 19
			for line in obj.checks_line:
				worksheet.merge_range('A' + str(check) + ':C' + str(check), line.name, table_left)
				worksheet.merge_range('D' + str(check) + ':E' + str(check), line.standard, table_center)
				worksheet.merge_range('F' + str(check) + ':G' + str(check), line.actual, table_center)
				check += 1
			
			worksheet.merge_range('I17:U17', 'PARAMETER MESIN (Pengecekan parameter)', company_format)
			worksheet.merge_range('I18:K18', 'Parameter', table_header)
			worksheet.write('L18', '0', table_header)
			worksheet.write('M18', '2', table_header)
			worksheet.write('N18', '4', table_header)
			worksheet.write('O18', '6', table_header)
			worksheet.write('P18', '8', table_header)
			worksheet.write('Q18', '10', table_header)
			worksheet.write('R18', '12', table_header)
			worksheet.merge_range('S18:U18', 'Notes', table_header)
			worksheet.merge_range('S19:U25', obj.parameter_mesin_notes or '', company_format)
			prod = 19
			for mesin in obj.params_mch_line:
				worksheet.merge_range('I' + str(prod)+':K' + str(prod), mesin.name, table_left)
				worksheet.write('L' + str(prod), mesin.param_0 or '', table_center)
				worksheet.write('M' + str(prod), mesin.param_2 or '', table_center)
				worksheet.write('N' + str(prod), mesin.param_4 or '', table_center)
				worksheet.write('O' + str(prod), mesin.param_6 or '', table_center)
				worksheet.write('P' + str(prod), mesin.param_8 or '', table_center)
				worksheet.write('Q' + str(prod), mesin.param_10 or '', table_center)
				worksheet.write('R' + str(prod), mesin.param_12 or '', table_center)
				prod +=1

			# silo = prod+2

			silo = check+1 if check > prod else prod+1
			worksheet.merge_range('A' + str(silo) + ':J' + str(silo), 'BOTTLE RECORD SILO ', company_format)
			worksheet.write('A' + str(silo+1), 'Type Silo', table_header)
			worksheet.merge_range('B' + str(silo+1) + ':D' + str(silo+1), 'Lot', table_header)
			worksheet.merge_range('E' + str(silo+1) + ':F' + str(silo+1), 'Supplier', table_header)
			worksheet.write('G' + str(silo+1), 'Time', table_center)
			worksheet.write('H' + str(silo+1), 'In', table_center)
			worksheet.write('I' + str(silo+1), 'Out', table_center)
			worksheet.write('J' + str(silo+1), 'Stock Akhir', table_center)
			

			total_in_a = 0; total_out_a = 0; total_end_a = 0
			silo += 1
			for bot_a in obj.bottle_record_silo_ids:
				type_silo = dict(bot_a._fields['silo_type'].selection).get(bot_a.silo_type) or ''
				time = '%02d:%02d' % (int(bot_a.time), bot_a.time % 1 * 60) or ''

				worksheet.write('A' + str(silo+1), type_silo, table_header)
				worksheet.merge_range('B' + str(silo+1) + ':D' + str(silo+1), bot_a.lot_id.name or '', table_header)
				worksheet.merge_range('E' + str(silo+1) + ':F' + str(silo+1), bot_a.supplier.name, table_header)
				worksheet.write('G' + str(silo+1), time, table_center)
				worksheet.write('H' + str(silo+1), bot_a.bottle_in or '', table_center)
				worksheet.write('I' + str(silo+1), bot_a.bottle_out or '', table_center)
				worksheet.write('J' + str(silo+1), bot_a.stock_akhir, table_center)
				total_in_a += bot_a.bottle_in; total_out_a += bot_a.bottle_out; total_end_a += bot_a.stock_akhir
				silo += 1

			silo += 1
			worksheet.merge_range('A' + str(silo) + ':G' + str(silo), 'Jumlah', table_header)
			worksheet.write('H' + str(silo), total_in_a, table_center)
			worksheet.write('I' + str(silo), total_out_a, table_center)
			worksheet.write('J' + str(silo), total_end_a, table_center)
			
			note_row = silo +1
			worksheet.merge_range('A' + str(note_row+1) + ':J' + str(note_row+5), obj.unscramble_note, company_format)
			# worksheet.merge_range('K' + str(note_row+1) + ':M' + str(note_row+4), '', table_header)
			# worksheet.merge_range('K' + str(note_row+5) + ':M' + str(note_row+5), 'Operator ', table_header)
			# worksheet.merge_range('N' + str(note_row+1) + ':P' + str(note_row+4), '', table_header)
			# worksheet.merge_range('N' + str(note_row+5) + ':P' + str(note_row+5), 'Shift leader', table_header)
			# worksheet.merge_range('Q' + str(note_row+1) + ':S' + str(note_row+4), '', table_header)
			# worksheet.merge_range('Q' + str(note_row+5) + ':S' + str(note_row+5), 'SPV/Manager', table_header)
