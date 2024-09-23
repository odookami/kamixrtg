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

class FillingXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_filling'
	_description = 'Daily Report Filling'
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
			worksheet.merge_range('E4:R5', 'Form Laporan Harian Filling (OBOL)', company_format)

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
			day = [v for k,v in data.items() if k == obj.dayofweek ][0]
			worksheet.merge_range('T8:U8', day, table_center)
			worksheet.merge_range('T9:U9', str(obj.date.strftime("%d-%m-%Y")), table_center)
			worksheet.merge_range('T10:U10', obj.shift, table_center)
			worksheet.merge_range('T11:U11', obj.team, table_center)
			worksheet.merge_range('T12:U12', obj.packaging, table_center)
			worksheet.merge_range('T13:U13', obj.line_machine, table_center)			    

			worksheet.merge_range('A7:Q7', 'GENERAL REPORT', company_format)
			worksheet.merge_range('A8:C8', 'CIP', table_left)
			worksheet.merge_range('A9:C9', 'Preparation', table_left)
			worksheet.merge_range('A10:C10', 'Total Breakdown', table_left)
			worksheet.merge_range('A11:C11', 'Running hours', table_left)
			worksheet.merge_range('A12:C12', 'Total Output / Shift', table_left)
			worksheet.merge_range('A13:C13', 'Total Output / Running', table_left)
			worksheet.merge_range('A14:C14', 'Total Reject', table_left)			

			worksheet.merge_range('D8:E8', obj.cip or '0', table_center)
			worksheet.merge_range('D9:E9', obj.preparation, table_center)
			worksheet.merge_range('D10:E10', obj.total_breakdown, table_center)
			worksheet.merge_range('D11:E11', obj.running_hours, table_center)
			worksheet.merge_range('D12:E12', obj.total_output_shift, table_center)
			worksheet.merge_range('D13:E13', obj.total_output_hours, table_center)
			worksheet.merge_range('D14:E14', obj.total_reject_produk, table_center)

			worksheet.write('F8', 'min', table_center)
			worksheet.write('F9', 'min', table_center)
			worksheet.write('F10', 'min', table_center)
			worksheet.write('F11', 'min', table_center)
			worksheet.write('F12', 'btl', table_center)
			worksheet.write('F13', 'min/btl', table_center)
			worksheet.write('F14', 'btl', table_center)
			
			worksheet.merge_range('G8:I8', 'NO. BO ', table_left)
			worksheet.merge_range('G9:I9', 'Product Name', table_left)
			worksheet.merge_range('G10:I10', 'Start Coding Btl', table_left)
			worksheet.merge_range('G11:I11', 'Finish Coding Btl', table_left)
			worksheet.merge_range('G12:I12', 'Output/Batch', table_left)
			worksheet.merge_range('G13:I13', 'Reject/Batch', table_left)
			c = 9
			general_line = [k for k in obj.batch_line]
			for i in general_line:
				sa = '%02d:%02d' % (int(i.start_coding), i.start_coding % 1 * 60)
				fa = '%02d:%02d' % (int(i.end_coding), i.end_coding % 1 * 60)
				worksheet.write(7, c, i.batch_number, table_center)
				worksheet.write(8, c, i.product_id.display_name, table_center)
				worksheet.write(9, c, sa, table_center)
				worksheet.write(10, c, fa, table_center)
				worksheet.write(11, c, i.output_batch, table_center)
				worksheet.write(12, c, i.reject_batch, table_center)
				c += 1
			# worksheet.merge_range('O8:Q8', 'Notes', company_format)
			# worksheet.merge_range('O9:Q13', obj.note or '', company_format)
# =========================================================================================       
			worksheet.merge_range('A15:R15', 'VERIFIKASI CODING BOTOL', company_format)
			worksheet.merge_range('A16:D17', 'Setting Coding Box (oleh QC) ', table_center)
			worksheet.merge_range('E16:H17', 'Actual Coding Coding Botol ', table_center)
			worksheet.merge_range('I16:L16', 'Cetak Coding oleh Produksi ', table_center)
			worksheet.merge_range('I17:J17', 'PIC ', table_center)
			worksheet.merge_range('K17:L17', 'Jam cetak coding ', table_center)
			worksheet.merge_range('M16:R16', 'Verifikasi Coding oleh QC ', table_center)
			worksheet.merge_range('M17:N17', 'PIC ', table_center)
			worksheet.merge_range('O17:P17', 'Jam cetak coding ', table_center)
			worksheet.merge_range('Q17:R17', 'Status ', table_center)
			worksheet.merge_range('S15:U15', 'Notes ', table_center)

			filestore_path = config.filestore(self._cr.dbname)
			row = 18
			pict = [i.actual_coding for i in obj.verify_coding_line]
			for coding in obj.verify_coding_line:
				worksheet.set_row(row-1, 60)
				self._cr.execute("""SELECT store_fname FROM ir_attachment WHERE res_model = '{}' AND res_id = {}""".format(coding._name,coding.id))
				fetch = self._cr.dictfetchone()
				img_file = open(filestore_path + "/" + fetch['store_fname'], 'rb')
				file_data = io.BytesIO(img_file.read())
				img_file.close()
				cc = '%02d:%02d' % (int(coding.jam_cetak_coding), coding.jam_cetak_coding % 1 * 60)
				ca = '%02d:%02d' % (int(coding.jam_verifikasi_coding), coding.jam_verifikasi_coding % 1 * 60)
				worksheet.merge_range('A' + str(row) + ':D' + str(row), coding.set_coding_by_qc, table_center)
				worksheet.insert_image('E' + str(row) + ':H' + str(row), 'file_data.jpeg', {'image_data': file_data,'x_scale': 0.5, 'y_scale': 0.3, 'x_offset':50})
				worksheet.merge_range('I' + str(row) + ':J' + str(row), coding.pic_produksi, table_center)
				worksheet.merge_range('K' + str(row) + ':L' + str(row), cc, table_center)
				worksheet.merge_range('M' + str(row) + ':N' + str(row), coding.pic_qc, table_center)
				worksheet.merge_range('O' + str(row) + ':P' + str(row), ca, table_center)
				worksheet.merge_range('Q' + str(row) + ':R' + str(row), coding.status_verifikasi, table_center)
				row += 1
			worksheet.merge_range('S16' + ':U'+ str(row-1), obj.note_vefiri_coding or '', table_center)
# # =========================================================================================     
			check = row +1
			worksheet.merge_range('A' + str(check) + ':U' + str(check), 'GENERAL CHECKS ( early shift checks)', company_format)

			cek_1 = check+1; cek_2 = check+1; step = check+1; note =check+1
			worksheet.merge_range('A' + str(cek_1) + ':C' + str(cek_1), 'Parameter', table_center)
			worksheet.merge_range('D' + str(cek_1) + ':E' + str(cek_1), 'Std', table_center)
			worksheet.write('F' + str(cek_1), 'Actual', table_center)
			worksheet.merge_range('G' + str(cek_2) + ':I' + str(cek_2), 'Parameter', table_center)
			worksheet.merge_range('J' + str(cek_2) + ':K' + str(cek_2), 'Std', table_center)
			worksheet.write('L' + str(cek_2), 'Actual', table_center)
			tot_row_check = len(obj.checks_line) / 2
			lrow = 1
			for check_1 in obj.checks_line:
				if lrow <= tot_row_check:
					worksheet.merge_range('A' + str(cek_1+1)+':C' + str(cek_1+1), check_1.name or '', table_left)
					worksheet.merge_range('D' + str(cek_1+1)+':E' + str(cek_1+1), check_1.standard or '', table_center)
					worksheet.write('F' + str(cek_1+1), check_1.actual or '', table_center)
					cek_1 +=1
				else:
					worksheet.merge_range('G' + str(cek_2+1)+':I' + str(cek_2+1), check_1.name or '', table_left)
					worksheet.merge_range('J' + str(cek_2+1)+':K' + str(cek_2+1), check_1.standard or '', table_center)
					worksheet.write('L' + str(cek_2+1), check_1.actual or '', table_center)
					cek_2 += 1
				lrow += 1
			
			worksheet.merge_range('M' + str(step) + ':P' + str(step), 'Current filling step', company_format)
			worksheet.merge_range('M' + str(step+1) + ':O' + str(step+1), 'Running production', table_left)
			worksheet.merge_range('M' + str(step+2) + ':O' + str(step+2), 'CIP ( what step)', table_left)
			worksheet.merge_range('M' + str(step+3) + ':O' + str(step+3), 'Preparation', table_left)
			worksheet.merge_range('M' + str(step+4) + ':O' + str(step+4), 'Other', table_left)

			worksheet.write('P' + str(step+1), obj.run_production or '', table_center)
			worksheet.write('P' + str(step+2), obj.cip or '', table_center)
			worksheet.write('P' + str(step+3), obj.prep_filling or '', table_center)
			worksheet.write('P' + str(step+4), obj.other or '', table_center)

			line_2 = step+6
			worksheet.merge_range('M' + str(line_2) + ':O' + str(line_2), 'Parameter', table_center)
			worksheet.merge_range('P' + str(line_2) + ':Q' + str(line_2), 'Start Vol', table_center)
			worksheet.merge_range('R' + str(line_2) + ':S' + str(line_2), 'End Vol', table_center)
			worksheet.merge_range('T' + str(line_2) + ':U' + str(line_2), 'Change Time', table_center)
			for ceks_2 in obj.checks_2_line:
				worksheet.merge_range('M' + str(line_2+1)+':O' + str(line_2+1), ceks_2.name or '', table_left)
				worksheet.merge_range('P' + str(line_2+1)+':Q' + str(line_2+1), ceks_2.start_vol or '', table_center)
				worksheet.merge_range('R' + str(line_2+1)+':S' + str(line_2+1), ceks_2.end_vol or '', table_center)
				worksheet.merge_range('T' + str(line_2+1)+':U' + str(line_2+1), ceks_2.change_time or '', table_center)
				line_2 +=1
			
			worksheet.merge_range('R' + str(note) + ':U' + str(note), 'Notes', table_center)
			worksheet.merge_range('R' + str(note+1) + ':U' + str(note+4), obj.general_check_notes or '', table_center)

			mesin = line_2 +3
			worksheet.merge_range('A' + str(mesin) + ':U' + str(mesin), 'PARAMETER MESIN (Pengecekan parameter dilakukan 1 jam sekali)', table_center)
			worksheet.merge_range('A' + str(mesin+1) + ':C' + str(mesin+1), 'Parameter', table_center)
			worksheet.write('D' + str(mesin+1), '1', table_center)
			worksheet.write('E' + str(mesin+1), '2', table_center)
			worksheet.write('F' + str(mesin+1), '3', table_center)
			worksheet.write('G' + str(mesin+1), '4', table_center)
			worksheet.write('H' + str(mesin+1), '5', table_center)
			worksheet.write('I' + str(mesin+1), '6', table_center)
			worksheet.write('J' + str(mesin+1), '7', table_center)
			worksheet.write('K' + str(mesin+1), '8', table_center)
			worksheet.write('L' + str(mesin+1), '9', table_center)
			worksheet.write('M' + str(mesin+1), '10', table_center)
			worksheet.write('N' + str(mesin+1), '11', table_center)
			worksheet.write('O' + str(mesin+1), '12', table_center)
			prod = mesin+2
			for mesin in obj.parameter_mesin_1_line:
				worksheet.merge_range('A' + str(prod) + ':C' + str(prod), mesin.name, table_left)
				worksheet.write('D' + str(prod), mesin.param_1 or '', table_center)
				worksheet.write('E' + str(prod), mesin.param_2 or '', table_center)
				worksheet.write('F' + str(prod), mesin.param_3 or '', table_center)
				worksheet.write('G' + str(prod), mesin.param_4 or '', table_center)
				worksheet.write('H' + str(prod), mesin.param_5 or '', table_center)
				worksheet.write('I' + str(prod), mesin.param_6 or '', table_center)
				worksheet.write('J' + str(prod), mesin.param_7 or '', table_center)
				worksheet.write('K' + str(prod), mesin.param_8 or '', table_center)
				worksheet.write('L' + str(prod), mesin.param_9 or '', table_center)
				worksheet.write('M' + str(prod), mesin.param_10 or '', table_center)
				worksheet.write('N' + str(prod), mesin.param_11 or '', table_center)
				worksheet.write('O' + str(prod), mesin.param_12 or '', table_center)
				prod +=1
			
			for tc in obj.parameter_mesin_2_line:
				worksheet.merge_range('A' + str(prod) + ':C' + str(prod),tc.name, table_left)
				worksheet.merge_range('D' + str(prod) + ':G' + str(prod),'start- finish :'+ str(tc.check_time1 or ''), table_left)
				worksheet.merge_range('H' + str(prod) + ':K' + str(prod),'start- finish :'+ str(tc.check_time2 or ''), table_left)
				worksheet.merge_range('L' + str(prod) + ':O' + str(prod),'start- finish :'+ str(tc.check_time3 or ''), table_left)
				prod +=1
			
			seal = prod
			worksheet.merge_range('A' + str(seal) + ':U' + str(seal), 'SEALER MACHINE', table_center)
			prod_1 = seal+1
			for mesin in obj.params_seal_line:
				worksheet.merge_range('A' + str(prod_1) + ':C' + str(prod_1), mesin.name, table_left)
				worksheet.write('D' + str(prod_1), mesin.param_1 or '', table_center)
				worksheet.write('E' + str(prod_1), mesin.param_2 or '', table_center)
				worksheet.write('F' + str(prod_1), mesin.param_3 or '', table_center)
				worksheet.write('G' + str(prod_1), mesin.param_4 or '', table_center)
				worksheet.write('H' + str(prod_1), mesin.param_5 or '', table_center)
				worksheet.write('I' + str(prod_1), mesin.param_6 or '', table_center)
				worksheet.write('J' + str(prod_1), mesin.param_7 or '', table_center)
				worksheet.write('K' + str(prod_1), mesin.param_8 or '', table_center)
				worksheet.write('L' + str(prod_1), mesin.param_9 or '', table_center)
				worksheet.write('M' + str(prod_1), mesin.param_10 or '', table_center)
				worksheet.write('N' + str(prod_1), mesin.param_11 or '', table_center)
				worksheet.write('O' + str(prod_1), mesin.param_12 or '', table_center)
				prod_1 +=1
			
			ci1 = prod_1 +1; ci2 = prod_1 +1; ci3 = prod_1 +1
			worksheet.merge_range('A' + str(ci1) + ':U' + str(ci1), 'Cleaning In Place (CIP)', table_center)
			lrow = 1
			for fill in obj.filling_cip_line:
				if lrow <= 3:
					worksheet.merge_range('A' + str(ci1+1)+':D' + str(ci1+1), fill.no + '. ' + fill.name or '', table_left)
					worksheet.merge_range('E' + str(ci1+1)+':F' + str(ci1+1), fill.actual or '', table_center)
					ci1 +=1
				elif lrow <= 6:
					worksheet.merge_range('G' + str(ci2+1)+':J' + str(ci2+1), fill.no + '. ' + fill.name or '', table_left)
					worksheet.merge_range('K' + str(ci2+1)+':L' + str(ci2+1), fill.actual or '', table_center)
					ci2 +=1
				else:
					worksheet.merge_range('M' + str(ci3+1)+':P' + str(ci3+1), fill.no + '. ' + fill.name or '', table_left)
					worksheet.merge_range('Q' + str(ci3+1)+':R' + str(ci3+1), fill.actual or '', table_center)
					ci3 += 1
				lrow += 1
			
			satop = ci1 +2; satop1 = ci1 +2; satop2 = ci1 +2; satop3 = ci1 +2; satop4 = ci1 +2; satop5 = ci1 +2; note = ci1+2
			worksheet.merge_range('A' + str(satop) + ':B' + str(satop), 'Pre- Rinse', table_center)
			worksheet.write('A' + str(satop+1), 'Start', table_center)
			worksheet.write('B' + str(satop+1), 'Stop', table_center)
			for cip in obj.pre_rinse_line:
				worksheet.write('A' + str(satop+2), '%02d:%02d' % (int(cip.pre_rinse_start), cip.pre_rinse_start % 1 * 60) or '', table_center)
				worksheet.write('B' + str(satop+2), '%02d:%02d' % (int(cip.pre_rinse_stop), cip.pre_rinse_stop % 1 * 60) or '', table_center)
				satop +=1

			worksheet.merge_range('C' + str(satop1) + ':D' + str(satop1), 'Caustic / Lye', table_center)
			worksheet.write('C' + str(satop1+1), 'Start', table_center)
			worksheet.write('D' + str(satop1+1), 'Stop', table_center)
			for cip1 in obj.caustic_lye_line:
				worksheet.write('C' + str(satop1+2), '%02d:%02d' % (int(cip1.caustic_lye_start), cip1.caustic_lye_start % 1 * 60) or '', table_center)
				worksheet.write('D' + str(satop1+2), '%02d:%02d' % (int(cip1.caustic_lye_stop), cip1.caustic_lye_stop % 1 * 60) or '', table_center)
				satop1 +=1

			worksheet.merge_range('E' + str(satop2) + ':F' + str(satop2), 'Intermediete rinse', table_center)
			worksheet.write('E' + str(satop2+1), 'Start', table_center)
			worksheet.write('F' + str(satop2+1), 'Stop', table_center)
			for cip2 in obj.intermediete_rinse_line:
				worksheet.write('E' + str(satop2+2), '%02d:%02d' % (int(cip2.inter_rinse_start), cip2.inter_rinse_start % 1 * 60) or '', table_center)
				worksheet.write('F' + str(satop2+2), '%02d:%02d' % (int(cip2.inter_rinse_stop), cip2.inter_rinse_stop % 1 * 60) or '', table_center)
				satop2 +=1

			worksheet.merge_range('G' + str(satop3) + ':H' + str(satop3), 'Acid', table_center)
			worksheet.write('G' + str(satop3+1), 'Start', table_center)
			worksheet.write('H' + str(satop3+1), 'Stop', table_center)
			for cip3 in obj.acid_line:
				worksheet.write('G' + str(satop3+2), '%02d:%02d' % (int(cip3.acid_start), cip3.acid_start % 1 * 60) or '', table_center)
				worksheet.write('H' + str(satop3+2), '%02d:%02d' % (int(cip3.acid_stop), cip3.acid_stop % 1 * 60) or '', table_center)
				satop3 +=1

			worksheet.merge_range('I' + str(satop4) + ':K' + str(satop4), 'Final Rinse', table_center)
			worksheet.write('I' + str(satop4+1), 'Start', table_center)
			worksheet.write('J' + str(satop4+1), 'Stop', table_center)
			worksheet.write('K' + str(satop4+1), 'Ph', table_center)
			for cip4 in obj.final_rinse_line:
				worksheet.write('I' + str(satop4+2), '%02d:%02d' % (int(cip4.final_rinse_start), cip4.final_rinse_start % 1 * 60) or '', table_center)
				worksheet.write('J' + str(satop4+2), '%02d:%02d' % (int(cip4.final_rinse_stop), cip4.final_rinse_stop % 1 * 60) or '', table_center)
				worksheet.write('K' + str(satop4+2), '%02d:%02d' % (int(cip4.final_rinse_ph), cip4.final_rinse_ph % 1 * 60) or '', table_center)
				satop4 +=1

			worksheet.merge_range('L' + str(satop5) + ':N' + str(satop5), 'Hot Water', table_center)
			worksheet.write('L' + str(satop5+1), 'Start', table_center)
			worksheet.write('M' + str(satop5+1), 'Stop', table_center)
			worksheet.write('N' + str(satop5+1), 'Ph', table_center)
			for cip5 in obj.hot_water_line:
				worksheet.write('L' + str(satop5+2), '%02d:%02d' % (int(cip5.hot_water_start), cip5.hot_water_start % 1 * 60) or '', table_center)
				worksheet.write('M' + str(satop5+2), '%02d:%02d' % (int(cip5.hot_water_stop), cip5.hot_water_stop % 1 * 60) or '', table_center)
				worksheet.write('N' + str(satop5+2), '%02d:%02d' % (int(cip5.hot_water_ph), cip5.hot_water_ph % 1 * 60) or '', table_center)
				satop5 +=1
			
			worksheet.merge_range('O' + str(note) + ':U' + str(note), 'Notes', table_center)
			worksheet.merge_range('O' + str(note+1) + ':U' + str(note+4), obj.cip_notes or '', table_center)

			cis1 = note +6; cis2 = note +6; cis3 = note +6
			worksheet.merge_range('A' + str(cis1) + ':U' + str(cis1), 'Preparation after CIP', table_center)
			lrow = 1
			for fills in obj.after_cip_line:
				if lrow <= 3:
					worksheet.merge_range('A' + str(cis1+1)+':D' + str(cis1+1), fills.no + '. ' + fills.name or '', table_left)
					worksheet.merge_range('E' + str(cis1+1)+':F' + str(cis1+1), fills.actual or '', table_center)
					cis1 +=1
				elif lrow <= 6:
					worksheet.merge_range('G' + str(cis2+1)+':J' + str(cis2+1), fills.no + '. ' + fills.name or '', table_left)
					worksheet.merge_range('K' + str(cis2+1)+':L' + str(cis2+1), fills.actual or '', table_center)
					cis2 +=1
				else:
					worksheet.merge_range('M' + str(cis3+1)+':P' + str(cis3+1), fills.no + '. ' + fills.name or '', table_left)
					worksheet.merge_range('Q' + str(cis3+1)+':R' + str(cis3+1), fills.actual or '', table_center)
					cis3 += 1
				lrow += 1
			
			foil = cis1 +2
			worksheet.merge_range('A' + str(foil) + ':J' + str(foil), 'ALLUFOIL USAGE', company_format)
			worksheet.merge_range('K' + str(foil) + ':U' + str(foil), 'ALLUFOIL RECORD', company_format)

			worksheet.merge_range('A' + str(foil+1) + ':B' + str(foil+1) , 'Time Change', table_center)
			worksheet.merge_range('C' + str(foil+1) + ':D' + str(foil+1) , 'Lot', table_center)
			worksheet.merge_range('E' + str(foil+1) + ':F' + str(foil+1), 'First Stock (Netto)', table_center)
			worksheet.merge_range('G' + str(foil+1) + ':H' + str(foil+1), 'Start', table_center)
			worksheet.merge_range('I' + str(foil+1) + ':J' + str(foil+1), 'Finish', table_center)
			worksheet.merge_range('K' + str(foil+1) + ':L' + str(foil+1), 'In Minutes', table_center)
			worksheet.write('M' + str(foil+1), 'Code Batch', table_center)
			worksheet.write('N' + str(foil+1), 'Out', table_center)
			worksheet.write('O' + str(foil+1), 'Reject', table_center)
			worksheet.write('P' + str(foil+1), 'Last Stock (Netto)', table_center)
			worksheet.write('Q' + str(foil+1), 'Return', table_center)
			worksheet.merge_range('R' + str(foil+1) + ':U' + str(foil+1), 'Notes', company_format)
			foil_line = foil+2
			for label in obj.material_line:
				worksheet.merge_range('A' + str(foil_line) + ':B' + str(foil_line), '%02d:%02d' % (int(label.time_change), label.time_change % 1 * 60) or '', table_center)
				worksheet.merge_range('C' + str(foil_line) + ':D' + str(foil_line), label.lot_id.name, table_center)
				worksheet.merge_range('E' + str(foil_line) + ':F' + str(foil_line), label.first_stock, table_center)
				worksheet.merge_range('G' + str(foil_line) + ':H' + str(foil_line), '%02d:%02d' % (int(label.start), label.start % 1 * 60) or '', table_center)
				worksheet.merge_range('I' + str(foil_line) + ':J' + str(foil_line), '%02d:%02d' % (int(label.finish), label.finish % 1 * 60) or '', table_center)
				worksheet.merge_range('K' + str(foil_line) + ':L' + str(foil_line), label.in_minute, table_center)
				worksheet.write('M' + str(foil_line), label.batch_code, table_center)
				worksheet.write('N' + str(foil_line), label.out_qty, table_center)
				worksheet.write('O' + str(foil_line), label.reject, table_center)
				worksheet.write('P' + str(foil_line), label.last_stock, table_center)
				worksheet.write('Q' + str(foil_line), label.return_qty, table_center)
				foil_line+=1
			worksheet.merge_range('R' + str(foil+2) + ':U' + str(foil_line-1), obj.material_usage_note or '', company_format)

			foil_line += 1
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
			worksheet.merge_range('A' + str(note_row+1) + ':I' + str(note_row+5), obj.filling_note, table_center)
			worksheet.merge_range('J' + str(note_row+1) + ':O' + str(note_row+4), '', table_header)
			worksheet.merge_range('J' + str(note_row+5) + ':O' + str(note_row+5), 'Operator: '+ obj.operator, table_header)
			worksheet.merge_range('P' + str(note_row+1) + ':U' + str(note_row+4), '', table_header)
			worksheet.merge_range('P' + str(note_row+5) + ':U' + str(note_row+5), 'Shift leader: '+ obj.leader, table_header)
