# -*- coding: utf-8 -*-

import io
import os
import base64
from dateutil import relativedelta
from datetime import date, datetime
from odoo.exceptions import ValidationError
from odoo import api, fields, models, SUPERUSER_ID, _
import time
import itertools
import xlsxwriter
import re
import string

class UnLoaderXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_unloader'
	_description = 'Daily Report UnLoader'
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
			worksheet.insert_image('A2:D5', FILE_DIR+FILE_NAME, {'x_scale': 1.5, 'y_scale': 1.5, 'x_offset':15})
			
			worksheet.merge_range('E2:R3', 'PRODUCTION DEPARTMENT', company_format)
			worksheet.merge_range('E4:R5', 'Form Laporan Harian UnLoader (OBOL)', company_format)

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
			# worksheet.merge_range('R14:U14', '', company_format)

			data = dict(obj.fields_get(['dayofweek'])['dayofweek']['selection'])
			if not obj.dayofweek:
				raise ValidationError(_('Mohon Isi Field Hari Terlebih Dahulu'))
			day = [v for k,v in data.items() if k == obj.dayofweek ][0]
			worksheet.merge_range('T8:U8', day, table_center)
			worksheet.merge_range('T9:U9', str(obj.date.strftime("%d-%m-%Y")), table_center)
			worksheet.merge_range('T10:U10', obj.shift, table_center)
			worksheet.merge_range('T11:U11', obj.team, table_center)
			worksheet.merge_range('T12:U12', obj.packaging, table_center)
			worksheet.merge_range('T13:U13', obj.line_machine, table_center)			    

			worksheet.merge_range('A7:Q7', 'GENERAL REPORT', company_format)
			worksheet.merge_range('A8:C8', 'Downtime', table_left)
			worksheet.merge_range('A9:C9', 'Total Breakdown', table_left)
			worksheet.merge_range('A10:C10', 'Running hours', table_left)
			worksheet.merge_range('A11:C11', 'Total Reject', table_left)			

			worksheet.merge_range('D8:E8', obj.preparation, table_center)
			worksheet.merge_range('D9:E9', obj.total_breakdown, table_center)
			worksheet.merge_range('D10:E10', obj.running_hours, table_center)
			worksheet.merge_range('D11:E11', obj.total_reject_produk, table_center)

			worksheet.write('F8', 'min', table_center)
			worksheet.write('F9', 'min', table_center)
			worksheet.write('F10', 'min', table_center)
			worksheet.write('F11', 'btl', table_center)
			
			worksheet.merge_range('G8:I8', 'NO. BO ', table_left)
			worksheet.merge_range('G9:I9', 'Product Name', table_left)
			worksheet.merge_range('G10:I10', 'Start Unloading Actual', table_left)
			worksheet.merge_range('G11:I11', 'Finish Unloading Actual', table_left)
			worksheet.merge_range('G12:I12', 'Reject/Batch Btl', table_left)
			c = 9
			general_line = [k for k in obj.batch_line]
			for i in general_line:
				sa = '%02d:%02d' % (int(i.start_coding), i.start_coding % 1 * 60)
				fa = '%02d:%02d' % (int(i.end_coding), i.end_coding % 1 * 60)
				worksheet.write(7, c, i.batch_number, table_center)
				worksheet.write(8, c, i.product_id.display_name, table_center)
				worksheet.write(9, c, sa, table_center)
				worksheet.write(10, c, fa, table_center)
				worksheet.write(11, c, i.reject_batch, table_center)
				c += 1
			worksheet.merge_range('A13:Q13', 'Notes', company_format)
			worksheet.merge_range('A14:Q16', obj.note or '', company_format)
			worksheet.merge_range('R14:U16', '', company_format)
# =========================================================================================       		
			check = 17
			worksheet.merge_range('A' + str(check) + ':U' + str(check), 'GENERAL CHECKS ( early shift checks)', company_format)

			cek_1 = check+1; cek_2 = check+1;
			worksheet.merge_range('A' + str(cek_1) + ':C' + str(cek_1), 'Parameter', table_center)
			worksheet.merge_range('D' + str(cek_1) + ':E' + str(cek_1), 'Std', table_center)
			worksheet.merge_range('F' + str(cek_1) + ':G' + str(cek_1), 'Actual', table_center)
			worksheet.merge_range('H' + str(cek_2) + ':J' + str(cek_2), 'Parameter', table_center)
			worksheet.merge_range('K' + str(cek_2) + ':L' + str(cek_2), 'Std', table_center)
			worksheet.merge_range('M' + str(cek_2) + ':N' + str(cek_2), 'Actual', table_center)
			tot_row_check = len(obj.checks_line) / 2
			lrow = 1
			if obj.checks_line:
				for check_1 in obj.checks_line:
					if lrow <= tot_row_check:
						worksheet.merge_range('A' + str(cek_1+1)+':C' + str(cek_1+1), check_1.name or '', table_left)
						worksheet.merge_range('D' + str(cek_1+1)+':E' + str(cek_1+1), check_1.standard or '', table_center)
						worksheet.merge_range('F' + str(cek_1+1) + ':G' + str(cek_1+1), check_1.actual or '', table_center)
						cek_1 +=1
					else:
						worksheet.merge_range('H' + str(cek_2+1)+':J' + str(cek_2+1), check_1.name or '', table_left)
						worksheet.merge_range('K' + str(cek_2+1)+':L' + str(cek_2+1), check_1.standard or '', table_center)
						worksheet.merge_range('M' + str(cek_2+1)+ ':N' + str(cek_2+1), check_1.actual or '', table_center)
						cek_2 += 1
					lrow += 1
			worksheet.merge_range('O18' + ':U18', 'Notes', table_center)
			worksheet.merge_range('O19' + ':U' + str(cek_2), obj.general_check_notes or '', table_center)
# =========================================================================================       					
			prod = 25
			worksheet.merge_range('A' + str(prod) + ':U' + str(prod), 'PRODUCTION RECORDS)', company_format)

			prod_1 = prod+1; prod_2 = prod+1; prod_3 = prod+1; prod_4 = prod+1; prod_5 = prod+1; prod_6 = prod+1; prod_8 = prod+1; prod_7 = prod+1; 
			if obj.prod_rec_1_line:
				if obj.batch_1:
					batch_1 = str(obj.batch_1)
				else:
					batch_1 = ''
				worksheet.merge_range('A' + str(prod_1) + ':B' + str(prod_1), 'Parameter -'+ batch_1 or '', table_center)
				worksheet.write('C' + str(prod_1), '1', table_center)
				worksheet.write('D' + str(prod_1), '2', table_center)
				worksheet.write('E' + str(prod_1), '3', table_center)
				worksheet.write('F' + str(prod_1), '4', table_center)
				worksheet.write('G' + str(prod_1), '5', table_center)
				worksheet.write('H' + str(prod_1), '6', table_center)
				worksheet.merge_range('I' + str(prod_1) + ':J' + str(prod_1), 'Note', table_center)
				prod_line_1 = prod_1+1
				for i in obj.prod_rec_1_line:
					pram_1 = '' if not i.param_1 else " =" if i.param_1 == "=" else i.param_1
					pram_6 = '' if not i.param_6 else " =" if i.param_6 == "=" else i.param_6
					worksheet.merge_range('A' + str(prod_line_1) + ':B' + str(prod_line_1), i.name, table_center)
					worksheet.write('C' + str(prod_line_1), pram_1 or '', table_center)
					worksheet.write('D' + str(prod_line_1), i.param_2 or '', table_center)
					worksheet.write('E' + str(prod_line_1), i.param_3 or '', table_center)
					worksheet.write('F' + str(prod_line_1), i.param_4 or '', table_center)
					worksheet.write('G' + str(prod_line_1), i.param_5 or '', table_center)
					worksheet.write('H' + str(prod_line_1), pram_6 or '', table_center)
					prod_line_1+=1
				worksheet.merge_range('I' + str(prod_1+1) + ':J' + str(prod_line_1-1), obj.batch_note_1 or '', table_center)

			if obj.prod_rec_2_line:
				worksheet.merge_range('L' + str(prod_2) + ':M' + str(prod_2), 'Parameter -'+ obj.batch_2 or '', table_center)
				worksheet.write('N' + str(prod_2), '1', table_center)
				worksheet.write('O' + str(prod_2), '2', table_center)
				worksheet.write('P' + str(prod_2), '3', table_center)
				worksheet.write('Q' + str(prod_2), '4', table_center)
				worksheet.write('R' + str(prod_2), '5', table_center)
				worksheet.write('S' + str(prod_2), '6', table_center)
				worksheet.merge_range('T' + str(prod_2) + ':U' + str(prod_2), 'Note', table_center)
				prod_line_2 = prod_2+1
				for i in obj.prod_rec_2_line:
					pram_1 = '' if not i.param_1 else " =" if i.param_1 == "=" else i.param_1
					pram_6 = '' if not i.param_6 else " =" if i.param_6 == "=" else i.param_6
					worksheet.merge_range('L' + str(prod_line_2) + ':M' + str(prod_line_2), i.name, table_center)
					worksheet.write('N' + str(prod_line_2), pram_1 or '', table_center)
					worksheet.write('O' + str(prod_line_2), i.param_2 or '', table_center)
					worksheet.write('P' + str(prod_line_2), i.param_3 or '', table_center)
					worksheet.write('Q' + str(prod_line_2), i.param_4 or '', table_center)
					worksheet.write('R' + str(prod_line_2), i.param_5 or '', table_center)
					worksheet.write('S' + str(prod_line_2), pram_6 or '', table_center)
					prod_line_2+=1
				worksheet.merge_range('T' + str(prod_2+1) + ':U' + str(prod_line_2-1), obj.batch_note_2 or '', table_center)
			
			if obj.prod_rec_3_line:
				prod_3 = prod_line_1+1
				worksheet.merge_range('A' + str(prod_3) + ':B' + str(prod_3), 'Parameter -'+ obj.batch_3 or '', table_center)
				worksheet.write('C' + str(prod_3), '1', table_center)
				worksheet.write('D' + str(prod_3), '2', table_center)
				worksheet.write('E' + str(prod_3), '3', table_center)
				worksheet.write('F' + str(prod_3), '4', table_center)
				worksheet.write('G' + str(prod_3), '5', table_center)
				worksheet.write('H' + str(prod_3), '6', table_center)
				worksheet.merge_range('I' + str(prod_3) + ':J' + str(prod_3), 'Note', table_center)
				prod_line_3 = prod_3+1
				for i in obj.prod_rec_3_line:
					pram_1 = '' if not i.param_1 else " =" if i.param_1 == "=" else i.param_1
					pram_6 = '' if not i.param_6 else " =" if i.param_6 == "=" else i.param_6
					worksheet.merge_range('A' + str(prod_line_3) + ':B' + str(prod_line_3), i.name, table_center)
					worksheet.write('C' + str(prod_line_3), pram_1 or '', table_center)
					worksheet.write('D' + str(prod_line_3), i.param_2 or '', table_center)
					worksheet.write('E' + str(prod_line_3), i.param_3 or '', table_center)
					worksheet.write('F' + str(prod_line_3), i.param_4 or '', table_center)
					worksheet.write('G' + str(prod_line_3), i.param_5 or '', table_center)
					worksheet.write('H' + str(prod_line_3), pram_6 or '', table_center)
					prod_line_3+=1
				worksheet.merge_range('I' + str(prod_3+1) + ':J' + str(prod_line_3-1), obj.batch_note_3 or '', table_center)

			if obj.prod_rec_4_line:
				prod_4 = prod_line_2+1
				worksheet.merge_range('L' + str(prod_4) + ':M' + str(prod_4), 'Parameter -'+ obj.batch_4 or '', table_center)
				worksheet.write('N' + str(prod_4), '1', table_center)
				worksheet.write('O' + str(prod_4), '2', table_center)
				worksheet.write('P' + str(prod_4), '3', table_center)
				worksheet.write('Q' + str(prod_4), '4', table_center)
				worksheet.write('R' + str(prod_4), '5', table_center)
				worksheet.write('S' + str(prod_4), '6', table_center)
				worksheet.merge_range('T' + str(prod_4) + ':U' + str(prod_4), 'Note', table_center)
				prod_line_4 = prod_4
				print(prod_line_4,'lalalala')
				for i in obj.prod_rec_4_line:
					prod_line_4+=1
					pram_1 = '' if not i.param_1 else " =" if i.param_1 == "=" else i.param_1
					pram_6 = '' if not i.param_6 else " =" if i.param_6 == "=" else i.param_6
					worksheet.merge_range('L' + str(prod_line_4) + ':M' + str(prod_line_4), i.name, table_center)
					worksheet.write('N' + str(prod_line_4), pram_1 or '', table_center)
					worksheet.write('O' + str(prod_line_4), i.param_2 or '', table_center)
					worksheet.write('P' + str(prod_line_4), i.param_3 or '', table_center)
					worksheet.write('Q' + str(prod_line_4), i.param_4 or '', table_center)
					worksheet.write('R' + str(prod_line_4), i.param_5 or '', table_center)
					worksheet.write('S' + str(prod_line_4), pram_6 or '', table_center)
				worksheet.merge_range('T' + str(prod_4+1) + ':U' + str(prod_line_4-1), obj.batch_note_4 or '', table_center)
			
			if obj.prod_rec_5_line:
				prod_5 = prod_line_4+1
				worksheet.merge_range('A' + str(prod_5) + ':B' + str(prod_5), 'Parameter -'+ obj.batch_5 or '', table_center)
				worksheet.write('C' + str(prod_5), '1', table_center)
				worksheet.write('D' + str(prod_5), '2', table_center)
				worksheet.write('E' + str(prod_5), '3', table_center)
				worksheet.write('F' + str(prod_5), '4', table_center)
				worksheet.write('G' + str(prod_5), '5', table_center)
				worksheet.write('H' + str(prod_5), '6', table_center)
				worksheet.merge_range('I' + str(prod_5) + ':J' + str(prod_5), 'Note', table_center)
				prod_line_5 = prod_5+1
				for i in obj.prod_rec_5_line:
					pram_1 = '' if not i.param_1 else " =" if i.param_1 == "=" else i.param_1
					pram_6 = '' if not i.param_6 else " =" if i.param_6 == "=" else i.param_6
					worksheet.merge_range('A' + str(prod_line_5) + ':B' + str(prod_line_5), i.name, table_center)
					worksheet.write('C' + str(prod_line_5), pram_1 or '', table_center)
					worksheet.write('D' + str(prod_line_5), i.param_2 or '', table_center)
					worksheet.write('E' + str(prod_line_5), i.param_3 or '', table_center)
					worksheet.write('F' + str(prod_line_5), i.param_4 or '', table_center)
					worksheet.write('G' + str(prod_line_5), i.param_5 or '', table_center)
					worksheet.write('H' + str(prod_line_5), pram_6 or '', table_center)
					prod_line_5+=1
				worksheet.merge_range('I' + str(prod_5+1) + ':J' + str(prod_line_5-1), obj.batch_note_5 or '', table_center)

			if obj.prod_rec_6_line:
				prod_6 = prod_line_4+1
				worksheet.merge_range('L' + str(prod_6) + ':M' + str(prod_6), 'Parameter -'+ obj.batch_6 or '', table_center)
				worksheet.write('N' + str(prod_6), '1', table_center)
				worksheet.write('O' + str(prod_6), '2', table_center)
				worksheet.write('P' + str(prod_6), '3', table_center)
				worksheet.write('Q' + str(prod_6), '4', table_center)
				worksheet.write('R' + str(prod_6), '5', table_center)
				worksheet.write('S' + str(prod_6), '6', table_center)
				worksheet.merge_range('T' + str(prod_6) + ':U' + str(prod_6), 'Note', table_center)
				prod_line_6 = prod_6+1
				for i in obj.prod_rec_6_line:
					pram_1 = '' if not i.param_1 else " =" if i.param_1 == "=" else i.param_1
					pram_6 = '' if not i.param_6 else " =" if i.param_6 == "=" else i.param_6
					worksheet.merge_range('L' + str(prod_line_6) + ':M' + str(prod_line_6), i.name, table_center)
					worksheet.write('N' + str(prod_line_6), pram_1 or '', table_center)
					worksheet.write('O' + str(prod_line_6), i.param_2 or '', table_center)
					worksheet.write('P' + str(prod_line_6), i.param_3 or '', table_center)
					worksheet.write('Q' + str(prod_line_6), i.param_4 or '', table_center)
					worksheet.write('R' + str(prod_line_6), i.param_5 or '', table_center)
					worksheet.write('S' + str(prod_line_6), pram_6 or '', table_center)
					prod_line_6+=1
				worksheet.merge_range('T' + str(prod_6+1) + ':U' + str(prod_line_6-1), obj.batch_note_6 or '', table_center)
			
			if obj.prod_rec_7_line:
				prod_7 = prod_line_6+1
				worksheet.merge_range('A' + str(prod_7) + ':B' + str(prod_7), 'Parameter -'+ obj.batch_7 or '', table_center)
				worksheet.write('C' + str(prod_7), '1', table_center)
				worksheet.write('D' + str(prod_7), '2', table_center)
				worksheet.write('E' + str(prod_7), '3', table_center)
				worksheet.write('F' + str(prod_7), '4', table_center)
				worksheet.write('G' + str(prod_7), '5', table_center)
				worksheet.write('H' + str(prod_7), '6', table_center)
				worksheet.merge_range('I' + str(prod_7) + ':J' + str(prod_7), 'Note', table_center)
				prod_line_7 = prod_7+1
				for i in obj.prod_rec_7_line:
					pram_1 = '' if not i.param_1 else " =" if i.param_1 == "=" else i.param_1
					pram_6 = '' if not i.param_6 else " =" if i.param_6 == "=" else i.param_6
					worksheet.merge_range('A' + str(prod_line_7) + ':B' + str(prod_line_7), i.name, table_center)
					worksheet.write('C' + str(prod_line_7), pram_1 or '', table_center)
					worksheet.write('D' + str(prod_line_7), i.param_2 or '', table_center)
					worksheet.write('E' + str(prod_line_7), i.param_3 or '', table_center)
					worksheet.write('F' + str(prod_line_7), i.param_4 or '', table_center)
					worksheet.write('G' + str(prod_line_7), i.param_5 or '', table_center)
					worksheet.write('H' + str(prod_line_7), pram_6 or '', table_center)
					prod_line_7+=1
				worksheet.merge_range('I' + str(prod_7+1) + ':J' + str(prod_line_7-1), obj.batch_note_7 or '', table_center)

			if obj.prod_rec_8_line:
				prod_8 = prod_line_6+1
				worksheet.merge_range('L' + str(prod_8) + ':M' + str(prod_8), 'Parameter -'+ obj.batch_8 or '', table_center)
				worksheet.write('N' + str(prod_8), '1', table_center)
				worksheet.write('O' + str(prod_8), '2', table_center)
				worksheet.write('P' + str(prod_8), '3', table_center)
				worksheet.write('Q' + str(prod_8), '4', table_center)
				worksheet.write('R' + str(prod_8), '5', table_center)
				worksheet.write('S' + str(prod_8), '6', table_center)
				worksheet.merge_range('T' + str(prod_8) + ':U' + str(prod_8), 'Note', table_center)
				prod_line_8 = prod_8+1
				for i in obj.prod_rec_8_line:
					pram_1 = '' if not i.param_1 else " =" if i.param_1 == "=" else i.param_1
					pram_6 = '' if not i.param_6 else " =" if i.param_6 == "=" else i.param_6
					worksheet.merge_range('L' + str(prod_line_8) + ':M' + str(prod_line_8), i.name, table_center)
					worksheet.write('N' + str(prod_line_8), pram_1 or '', table_center)
					worksheet.write('O' + str(prod_line_8), i.param_2 or '', table_center)
					worksheet.write('P' + str(prod_line_8), i.param_3 or '', table_center)
					worksheet.write('Q' + str(prod_line_8), i.param_4 or '', table_center)
					worksheet.write('R' + str(prod_line_8), i.param_5 or '', table_center)
					worksheet.write('S' + str(prod_line_8), pram_6 or '', table_center)
					prod_line_8+=1
				worksheet.merge_range('T' + str(prod_8+1) + ':U' + str(prod_line_8-1), obj.batch_note_8 or '', table_center)
						
# =========================================================================================
			l = [prod_line_1 if obj.prod_rec_1_line else 0, prod_line_3 if obj.prod_rec_3_line else 0,prod_line_5 if obj.prod_rec_5_line else 0,prod_line_7 if obj.prod_rec_7_line else 0]
			foil_line =  max(l) + 1
			worksheet.merge_range('A' + str(foil_line) + ':O' + str(foil_line), 'CATATAN KETIDAKSESUAIAN SELAMA PROSES PRODUKSI' , table_center)
			worksheet.merge_range('A' + str(foil_line+1) + ':B' + str(foil_line+1), 'Start', table_center)
			worksheet.merge_range('C' + str(foil_line+1) + ':D' + str(foil_line+1), 'Finish', table_center)
			worksheet.merge_range('E' + str(foil_line+1) + ':F' + str(foil_line+1), 'Total', table_center)
			worksheet.merge_range('G' + str(foil_line+1) + ':I' + str(foil_line+1), 'Uraian Masalah', table_center)
			worksheet.merge_range('J' + str(foil_line+1) + ':K' + str(foil_line+1), 'Frekuensi', table_center)
			worksheet.merge_range('L' + str(foil_line+1) + ':M' + str(foil_line+1), 'Status', table_center)
			worksheet.merge_range('N' + str(foil_line+1) + ':O' + str(foil_line+1), 'PIC', table_center)
			for inco in obj.incompatibility_line:
				start = '%02d:%02d' % (int(inco.start), inco.start % 1 * 60)
				finish = '%02d:%02d' % (int(inco.finish), inco.finish % 1 * 60)
				total = '%02d:%02d' % (int(inco.total), inco.total % 1 * 60)
				worksheet.merge_range('A' + str(foil_line+2) + ':B' + str(foil_line+2), start, table_center)
				worksheet.merge_range('C' + str(foil_line+2) + ':D' + str(foil_line+2), finish, table_center)
				worksheet.merge_range('E' + str(foil_line+2) + ':F' + str(foil_line+2), total, table_center)
				worksheet.merge_range('G' + str(foil_line+2) + ':I' + str(foil_line+2), inco.uraian_masalah, table_center)
				worksheet.merge_range('J' + str(foil_line+2) + ':K' + str(foil_line+2), inco.frekuensi, table_center)
				worksheet.merge_range('L' + str(foil_line+2) + ':M' + str(foil_line+2), inco.status, table_center)
				worksheet.merge_range('N' + str(foil_line+2) + ':O' + str(foil_line+2), inco.pic, table_center)
				foil_line +=1

			note_row = foil_line +2
			worksheet.merge_range('A' + str(note_row+1) + ':I' + str(note_row+5), obj.unloader_note, table_center)
			worksheet.merge_range('J' + str(note_row+1) + ':O' + str(note_row+4), '', table_header)
			worksheet.merge_range('J' + str(note_row+5) + ':O' + str(note_row+5), 'Operator: '+ obj.operator, table_header)
			worksheet.merge_range('P' + str(note_row+1) + ':U' + str(note_row+4), '', table_header)
			worksheet.merge_range('P' + str(note_row+5) + ':U' + str(note_row+5), 'Shift leader: '+ obj.leader, table_header)