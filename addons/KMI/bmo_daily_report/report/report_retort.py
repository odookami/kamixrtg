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

class PackingXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_retort'
	_description = 'Daily Report Packing'
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

			worksheet.merge_range('A2:D5', '', company_format)
			worksheet.insert_image('A2:D5', FILE_DIR+FILE_NAME, {'x_scale': 1.5, 'y_scale': 1.5, 'x_offset':20})
			
			worksheet.merge_range('E2:R3', 'PRODUCTION DEPARTMENT', company_format)
			worksheet.merge_range('E4:R5', 'Form Laporan Harian Retort (OBOL)', company_format)

			worksheet.merge_range('S2:U2', 'No Dok: ' + obj.name, table_left)
			worksheet.merge_range('S3:U3', 'Tanggal: ' + str(obj.release_date.strftime("%d-%m-%Y")), table_left)
			worksheet.merge_range('S4:U4', 'Hal: ', table_left)
			worksheet.merge_range('S5:U5', 'Revisi: '+ str(obj.revision), table_left)
# =========================================================================================        

			worksheet.merge_range('R7:U7', 'Production Notes', company_format)
			worksheet.merge_range('R8:S8', 'Hari', table_left)
			worksheet.merge_range('R9:S9', 'Tanggal', table_left)
			worksheet.merge_range('R10:S10', 'Shift', table_left)
			worksheet.merge_range('R11:S11', 'Team', table_left)
			worksheet.merge_range('R12:S12', 'Kemasan (ml)', table_left)
			worksheet.merge_range('R13:S13', 'Line Machine', table_left)
			worksheet.merge_range('R14:U14', '', company_format)

			data = dict(obj.fields_get(['dayofweek'])['dayofweek']['selection'])
			day = [v for k,v in data.items() if k == obj.dayofweek ][0]
			worksheet.merge_range('T8:U8', day, table_center)
			worksheet.merge_range('T9:U9', str(obj.date.strftime("%d-%m-%Y")), table_center)
			worksheet.merge_range('T10:U10', obj.shift, table_center)
			worksheet.merge_range('T11:U11', obj.team, table_center)
			worksheet.merge_range('T12:U12', obj.packaging, table_center)
			worksheet.merge_range('T13:U13', obj.line_machine, table_center)			    

			worksheet.merge_range('A7:Q7', 'GENERAL REPORT', company_format)
			worksheet.merge_range('A8:C8', 'Preparation', table_left)
			worksheet.merge_range('A9:C9', 'Total Breakdown', table_left)
			worksheet.merge_range('A10:C10', 'Running hours', table_left)

			worksheet.merge_range('D8:E8', obj.preparation, table_center)
			worksheet.merge_range('D9:E9', obj.total_breakdown, table_center)
			worksheet.merge_range('D10:E10', obj.running_hours, table_center)

			worksheet.write('F8', 'min', table_center)
			worksheet.write('F9', 'min', table_center)
			worksheet.write('F10', 'min', table_center)

			worksheet.merge_range('G8:I8', 'NO. BO ', table_left)
			worksheet.merge_range('G9:I9', 'Variant', table_left)
			worksheet.merge_range('G10:I10', 'Start ', table_left)
			worksheet.merge_range('G11:I11', 'Finish  ', table_left)
			c = 9
			general_line = [k for k in obj.batch_line]
			for i in general_line:
				sa = '%02d:%02d' % (int(i.start_coding), i.start_coding % 1 * 60)
				fa = '%02d:%02d' % (int(i.end_coding), i.end_coding % 1 * 60)
				worksheet.write(7, c, i.batch_number, table_center)
				worksheet.write(8, c, i.product_id.display_name, table_center)
				worksheet.write(9, c, sa, table_center)
				worksheet.write(10, c, fa, table_center)
				c += 1
			worksheet.merge_range('A12:Q12', 'Notes', table_center)
			worksheet.merge_range('A13:Q14', obj.note or '', company_format)
# =========================================================================================       
			check = 16
			worksheet.merge_range('A' + str(check) + ':L' + str(check), 'GENERAL CHECKS ( early shift checks)', company_format)
			worksheet.merge_range('H' + str(check+1) + ':L' + str(check+1), 'Notes', table_center)

			cek_1 = check+1
			worksheet.merge_range('A' + str(cek_1) + ':C' + str(cek_1), 'Parameter', table_center)
			worksheet.merge_range('D' + str(cek_1) + ':E' + str(cek_1), 'Std', table_center)
			worksheet.merge_range('F' + str(cek_1) + ':G' + str(cek_1), 'Actual', table_center)
			for check_1 in obj.checks_line:
				worksheet.merge_range('A' + str(cek_1+1)+':C' + str(cek_1+1), check_1.name or '', table_left)
				worksheet.merge_range('D' + str(cek_1+1)+':E' + str(cek_1+1), check_1.standard or '', table_center)
				worksheet.merge_range('F' + str(cek_1+1) + ':G' + str(cek_1+1), check_1.actual or '', table_center)
				cek_1 +=1
			worksheet.merge_range('H' + str(check+2) + ':L' + str(cek_1), obj.note_checks or '', company_format)
				
			prod = cek_1 + 2
			worksheet.merge_range('A' + str(prod) + ':U' + str(prod), 'PRODUCTION RECORD', table_center)

			pro_1 = prod+1
			worksheet.merge_range('A' + str(pro_1) + ':C' + str(pro_1), 'Parameter ' + str(obj.batch_1 or ''), table_center)
			worksheet.merge_range('D' + str(pro_1) + ':E' + str(pro_1), '1', table_center)
			worksheet.merge_range('F' + str(pro_1) + ':G' + str(pro_1), '2', table_center)
			worksheet.merge_range('H' + str(pro_1) + ':I' + str(pro_1), '3', table_center)
			worksheet.merge_range('J' + str(pro_1) + ':K' + str(pro_1), '4', table_center)
			worksheet.merge_range('L' + str(pro_1) + ':M' + str(pro_1), '5', table_center)
			worksheet.merge_range('N' + str(pro_1) + ':O' + str(pro_1), '6', table_center)
			worksheet.merge_range('P' + str(pro_1) + ':Q' + str(pro_1), '7', table_center)
			worksheet.merge_range('R' + str(pro_1) + ':U' + str(pro_1), 'Notes', table_center)
			pro_line_1 = pro_1+1
			for prods_1 in obj.prod_rec_1_line:
				worksheet.merge_range('A' + str(pro_line_1) + ':C' + str(pro_line_1), prods_1.name, table_left)
				worksheet.merge_range('D' + str(pro_line_1) + ':E' + str(pro_line_1), prods_1.param_1 or '', table_center)
				worksheet.merge_range('F' + str(pro_line_1) + ':G' + str(pro_line_1), prods_1.param_2 or '', table_center)
				worksheet.merge_range('H' + str(pro_line_1) + ':I' + str(pro_line_1), prods_1.param_3 or '', table_center)
				worksheet.merge_range('J' + str(pro_line_1) + ':K' + str(pro_line_1), prods_1.param_4 or '', table_center)
				worksheet.merge_range('L' + str(pro_line_1) + ':M' + str(pro_line_1), prods_1.param_5 or '', table_center)
				worksheet.merge_range('N' + str(pro_line_1) + ':O' + str(pro_line_1), prods_1.param_6 or '', table_center)
				worksheet.merge_range('P' + str(pro_line_1) + ':Q' + str(pro_line_1), prods_1.param_7 or '', table_center)
				pro_line_1 += 1
			worksheet.merge_range('R' + str(pro_1+1) + ':U' + str(pro_line_1-1), obj.batch_note_1 or '', company_format)

			if obj.prod_rec_2_line:
				pro_2 = pro_line_1+1
				worksheet.merge_range('A' + str(pro_2) + ':C' + str(pro_2), 'Parameter ' + str(obj.batch_2 or ''), table_center)
				worksheet.merge_range('D' + str(pro_2) + ':E' + str(pro_2), '8', table_center)
				worksheet.merge_range('F' + str(pro_2) + ':G' + str(pro_2), '9', table_center)
				worksheet.merge_range('H' + str(pro_2) + ':I' + str(pro_2), '10', table_center)
				worksheet.merge_range('J' + str(pro_2) + ':K' + str(pro_2), '11', table_center)
				worksheet.merge_range('L' + str(pro_2) + ':M' + str(pro_2), '12', table_center)
				worksheet.merge_range('N' + str(pro_2) + ':O' + str(pro_2), '13', table_center)
				worksheet.merge_range('P' + str(pro_2) + ':Q' + str(pro_2), '14', table_center)
				worksheet.merge_range('R' + str(pro_2) + ':U' + str(pro_2), 'Notes', table_center)
				pro_line_2 = pro_2+1
				for prods_2 in obj.prod_rec_2_line:
					worksheet.merge_range('A' + str(pro_line_2) + ':C' + str(pro_line_2), prods_2.name, table_left)
					worksheet.merge_range('D' + str(pro_line_2) + ':E' + str(pro_line_2), prods_2.param_8 or '', table_center)
					worksheet.merge_range('F' + str(pro_line_2) + ':G' + str(pro_line_2), prods_2.param_9 or '', table_center)
					worksheet.merge_range('H' + str(pro_line_2) + ':I' + str(pro_line_2), prods_2.param_10 or '', table_center)
					worksheet.merge_range('J' + str(pro_line_2) + ':K' + str(pro_line_2), prods_2.param_11 or '', table_center)
					worksheet.merge_range('L' + str(pro_line_2) + ':M' + str(pro_line_2), prods_2.param_12 or '', table_center)
					worksheet.merge_range('N' + str(pro_line_2) + ':O' + str(pro_line_2), prods_2.param_13 or '', table_center)
					worksheet.merge_range('P' + str(pro_line_2) + ':Q' + str(pro_line_2), prods_2.param_14 or '', table_center)
					pro_line_2 += 1
				worksheet.merge_range('R' + str(pro_2+1) + ':U' + str(pro_line_2-1), obj.batch_note_2 or '', company_format)

			if obj.prod_rec_3_line:
				pro_3 = pro_line_2+1
				worksheet.merge_range('A' + str(pro_3) + ':C' + str(pro_3), 'Parameter ' + str(obj.batch_3 or ''), table_center)
				worksheet.merge_range('D' + str(pro_3) + ':E' + str(pro_3), '15', table_center)
				worksheet.merge_range('F' + str(pro_3) + ':G' + str(pro_3), '16', table_center)
				worksheet.merge_range('H' + str(pro_3) + ':I' + str(pro_3), '17', table_center)
				worksheet.merge_range('J' + str(pro_3) + ':K' + str(pro_3), '18', table_center)
				worksheet.merge_range('L' + str(pro_3) + ':M' + str(pro_3), '19', table_center)
				worksheet.merge_range('N' + str(pro_3) + ':O' + str(pro_3), '20', table_center)
				worksheet.merge_range('P' + str(pro_3) + ':Q' + str(pro_3), '21', table_center)
				worksheet.merge_range('R' + str(pro_3) + ':U' + str(pro_3), 'Notes', table_center)
				pro_line_3 = pro_3+1
				for prods_3 in obj.prod_rec_3_line:
					worksheet.merge_range('A' + str(pro_line_3) + ':C' + str(pro_line_3), prods_3.name, table_left)
					worksheet.merge_range('D' + str(pro_line_3) + ':E' + str(pro_line_3), prods_3.param_15 or '', table_center)
					worksheet.merge_range('F' + str(pro_line_3) + ':G' + str(pro_line_3), prods_3.param_16 or '', table_center)
					worksheet.merge_range('H' + str(pro_line_3) + ':I' + str(pro_line_3), prods_3.param_17 or '', table_center)
					worksheet.merge_range('J' + str(pro_line_3) + ':K' + str(pro_line_3), prods_3.param_18 or '', table_center)
					worksheet.merge_range('L' + str(pro_line_3) + ':M' + str(pro_line_3), prods_3.param_19 or '', table_center)
					worksheet.merge_range('N' + str(pro_line_3) + ':O' + str(pro_line_3), prods_3.param_20 or '', table_center)
					worksheet.merge_range('P' + str(pro_line_3) + ':Q' + str(pro_line_3), prods_3.param_21 or '', table_center)
					pro_line_3 += 1
				worksheet.merge_range('R' + str(pro_3+1) + ':U' + str(pro_line_3-1), obj.batch_note_3 or '', company_format)

			if obj.prod_rec_4_line:
				pro_4 = pro_line_3+1
				worksheet.merge_range('A' + str(pro_4) + ':C' + str(pro_4), 'Parameter ' + str(obj.batch_4 or ''), table_center)
				worksheet.merge_range('D' + str(pro_4) + ':E' + str(pro_4), '22', table_center)
				worksheet.merge_range('F' + str(pro_4) + ':G' + str(pro_4), '23', table_center)
				worksheet.merge_range('H' + str(pro_4) + ':I' + str(pro_4), '24', table_center)
				worksheet.merge_range('J' + str(pro_4) + ':K' + str(pro_4), '25', table_center)
				worksheet.merge_range('L' + str(pro_4) + ':M' + str(pro_4), '26', table_center)
				worksheet.merge_range('N' + str(pro_4) + ':O' + str(pro_4), '27', table_center)
				worksheet.merge_range('P' + str(pro_4) + ':Q' + str(pro_4), '28', table_center)
				worksheet.merge_range('R' + str(pro_4) + ':U' + str(pro_4), 'Notes', table_center)
				pro_line_4 = pro_4+1
				for prods_4 in obj.prod_rec_4_line:
					worksheet.merge_range('A' + str(pro_line_4) + ':C' + str(pro_line_4), prods_4.name, table_left)
					worksheet.merge_range('D' + str(pro_line_4) + ':E' + str(pro_line_4), prods_4.param_22 or '', table_center)
					worksheet.merge_range('F' + str(pro_line_4) + ':G' + str(pro_line_4), prods_4.param_23 or '', table_center)
					worksheet.merge_range('H' + str(pro_line_4) + ':I' + str(pro_line_4), prods_4.param_24 or '', table_center)
					worksheet.merge_range('J' + str(pro_line_4) + ':K' + str(pro_line_4), prods_4.param_25 or '', table_center)
					worksheet.merge_range('L' + str(pro_line_4) + ':M' + str(pro_line_4), prods_4.param_26 or '', table_center)
					worksheet.merge_range('N' + str(pro_line_4) + ':O' + str(pro_line_4), prods_4.param_27 or '', table_center)
					worksheet.merge_range('P' + str(pro_line_4) + ':Q' + str(pro_line_4), prods_4.param_28 or '', table_center)
					pro_line_4 += 1
				worksheet.merge_range('R' + str(pro_4+1) + ':U' + str(pro_line_4-1), obj.batch_note_4 or '', company_format)
			
			bigger = sorted([pro_line_1, pro_line_2 if obj.prod_rec_2_line else 0, pro_line_3 if obj.prod_rec_3_line else 0, pro_line_4 if obj.prod_rec_4_line else 0])
			ma = bigger[-1]+1

			worksheet.merge_range('A' + str(ma) + ':O' + str(ma), 'CATATAN KETIDAKSESUAIAN SELAMA PROSES PRODUKSI' , company_format)
			worksheet.merge_range('A' + str(ma+1) + ':B' + str(ma+1), 'Start', table_center)
			worksheet.merge_range('C' + str(ma+1) + ':D' + str(ma+1), 'Finish', table_center)
			worksheet.merge_range('E' + str(ma+1) + ':F' + str(ma+1), 'Total', table_center)
			worksheet.merge_range('G' + str(ma+1) + ':I' + str(ma+1), 'Uraian Masalah', table_center)
			worksheet.merge_range('J' + str(ma+1) + ':K' + str(ma+1), 'Frekuensi', table_center)
			worksheet.merge_range('L' + str(ma+1) + ':M' + str(ma+1), 'Status', table_center)
			worksheet.merge_range('N' + str(ma+1) + ':O' + str(ma+1), 'PIC', table_center)
			for inco in obj.incompatibility_line:
				start = '%02d:%02d' % (int(inco.start), inco.start % 1 * 60)
				finish = '%02d:%02d' % (int(inco.finish), inco.finish % 1 * 60)
				total = '%02d:%02d' % (int(inco.total), inco.total % 1 * 60)
				worksheet.merge_range('A' + str(ma+2) + ':B' + str(ma+2), start, table_center)
				worksheet.merge_range('C' + str(ma+2) + ':D' + str(ma+2), finish, table_center)
				worksheet.merge_range('E' + str(ma+2) + ':F' + str(ma+2), total, table_center)
				worksheet.merge_range('G' + str(ma+2) + ':I' + str(ma+2), inco.uraian_masalah, table_center)
				worksheet.merge_range('J' + str(ma+2) + ':K' + str(ma+2), inco.frekuensi, table_center)
				worksheet.merge_range('L' + str(ma+2) + ':M' + str(ma+2), inco.status, table_center)
				worksheet.merge_range('N' + str(ma+2) + ':O' + str(ma+2), inco.pic, table_center)
				ma +=1
			
			note_row = ma +2
			worksheet.merge_range('A' + str(note_row+1) + ':I' + str(note_row+5), obj.retort_note, company_format)
			worksheet.merge_range('J' + str(note_row+1) + ':M' + str(note_row+4), '', table_header)
			worksheet.merge_range('J' + str(note_row+5) + ':M' + str(note_row+5), 'Operator: '+ obj.operator, table_header)
			worksheet.merge_range('N' + str(note_row+1) + ':Q' + str(note_row+4), '', table_header)
			worksheet.merge_range('N' + str(note_row+5) + ':Q' + str(note_row+5), 'Shift leader: '+ obj.leader, table_header)
			worksheet.merge_range('R' + str(note_row+1) + ':U' + str(note_row+4), '', table_header)
			worksheet.merge_range('R' + str(note_row+5) + ':U' + str(note_row+5), 'SPV/Manager: ', table_header)
