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

class LabelingXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_labeling'
	_description = 'Daily Report Labeling'
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
			worksheet.merge_range('E4:R5', 'Form Laporan Harian Labeling (OBOL)', company_format)

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
			worksheet.merge_range('A8:C8', 'Preparation', table_left)
			worksheet.merge_range('A9:C9', 'Total Breakdown', table_left)
			worksheet.merge_range('A10:C10', 'Running hours', table_left)
			worksheet.merge_range('A11:C11', 'Total output', table_left)			
			worksheet.merge_range('A12:C12', 'Total reject  produk', table_left)
			worksheet.merge_range('A13:C13', 'Total reject carton', table_left)

			worksheet.merge_range('D8:E8', obj.preparation, table_center)
			worksheet.merge_range('D9:E9', obj.total_breakdown, table_center)
			worksheet.merge_range('D10:E10', obj.running_hours, table_center)
			worksheet.merge_range('D11:E11', obj.total_output, table_center)
			worksheet.merge_range('D12:E12', obj.total_reject_btl, table_center)
			worksheet.merge_range('D13:E13', obj.total_reject_lbl, table_center)

			worksheet.write('F8', 'min', table_center)
			worksheet.write('F9', 'min', table_center)
			worksheet.write('F10', 'min', table_center)
			worksheet.write('F11', 'btl', table_center)
			worksheet.write('F12', 'pcs', table_center)
			worksheet.write('F13', 'btl', table_center)
			
			worksheet.merge_range('G8:I8', 'NO. BO ', table_left)
			worksheet.merge_range('G9:I9', 'Variant', table_left)
			worksheet.merge_range('G10:I10', 'Start Aktual', table_left)
			worksheet.merge_range('G11:I11', 'Finish Aktual ', table_left)
			worksheet.merge_range('G12:I12', 'Output / batch (btl)', table_left)
			worksheet.merge_range('G13:I13', 'Reject / batch (btl)', table_left)
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
			worksheet.merge_range('O8:Q8', 'Notes', company_format)
			worksheet.merge_range('O9:Q13', obj.note or '', company_format)
# =========================================================================================       
			worksheet.merge_range('A15:R15', 'VERIFIKASI CODING LEHER (setiap ganti BO)', company_format)
			worksheet.merge_range('A16:D17', 'Setting Coding Box (oleh QC) ', table_center)
			worksheet.merge_range('E16:H17', 'Coding Leher Botol ', table_center)
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

			check = row +1
			worksheet.merge_range('A' + str(check) + ':L' + str(check), 'GENERAL CHECKS ( early shift checks)', company_format)
			worksheet.merge_range('H' + str(check+8) + ':L' + str(check+8), 'Notes', table_center)

			cek_1 = check+1
			worksheet.merge_range('A' + str(cek_1) + ':C' + str(cek_1), 'Parameter', table_center)
			worksheet.merge_range('D' + str(cek_1) + ':E' + str(cek_1), 'Std', table_center)
			worksheet.merge_range('F' + str(cek_1) + ':G' + str(cek_1), 'Actual', table_center)
			for check_1 in obj.checks_line_1:
				worksheet.merge_range('A' + str(cek_1+1)+':C' + str(cek_1+1), check_1.name or '', table_left)
				worksheet.merge_range('D' + str(cek_1+1)+':E' + str(cek_1+1), check_1.standard or '', table_center)
				worksheet.merge_range('F' + str(cek_1+1) + ':G' + str(cek_1+1), check_1.actual or '', table_center)
				cek_1 +=1
			worksheet.merge_range('H' + str(check+9) + ':L' + str(cek_1), obj.note_checks or '', company_format)
			
			cek_2 = check+1
			worksheet.write('H' + str(cek_2), 'Item', table_center)
			worksheet.write('I' + str(cek_2), 'start vol', table_center)
			worksheet.write('J' + str(cek_2), 'End Vol', table_center)
			worksheet.write('K' + str(cek_2), 'Change Time', table_center)
			worksheet.write('L' + str(cek_2), 'VJ-B', table_center)
			for check_2 in obj.checks_line_2:
				worksheet.write('H' + str(cek_2+1), check_2.item or '', table_center)
				worksheet.write('I' + str(cek_2+1), check_2.start_vol or '', table_center)
				worksheet.write('J' + str(cek_2+1), check_2.end_vol or '', table_center)
				worksheet.write('K' + str(cek_2+1), check_2.change_time or '', table_center)
				worksheet.write('L' + str(cek_2+1), check_2.vjb or '', table_center)
				cek_2 +=1
			
			mesin = cek_1 + 2
			worksheet.merge_range('A' + str(mesin) + ':U' + str(mesin), 'PARAMETER MESIN (Pengecekan parameter dilakukan 1 jam sekali)', table_center)
			pro_1 = mesin+1
			worksheet.merge_range('A' + str(pro_1) + ':C' + str(pro_1), 'Parameter', table_center)
			worksheet.write('D' + str(pro_1), '1', table_center)
			worksheet.write('E' + str(pro_1), '2', table_center)
			worksheet.write('F' + str(pro_1), '3', table_center)
			worksheet.write('G' + str(pro_1), '4', table_center)
			worksheet.write('H' + str(pro_1), '5', table_center)
			worksheet.write('I' + str(pro_1), '6', table_center)
			worksheet.write('J' + str(pro_1), '7', table_center)
			worksheet.write('K' + str(pro_1), '8', table_center)
			worksheet.write('L' + str(pro_1), '9', table_center)
			worksheet.write('M' + str(pro_1), '10', table_center)
			worksheet.write('N' + str(pro_1), '11', table_center)
			worksheet.write('O' + str(pro_1), '12', table_center)
			worksheet.write('P' + str(pro_1), '13', table_center)
			worksheet.write('Q' + str(pro_1), '14', table_center)
			worksheet.merge_range('R' + str(pro_1) + ':U' + str(pro_1), 'Notes', table_center)
			mesin_line_1 = pro_1+1
			for mesins_1 in obj.params_mch_line:
				worksheet.merge_range('A' + str(mesin_line_1) + ':C' + str(mesin_line_1), mesins_1.name, table_left)
				worksheet.write('D' + str(mesin_line_1), mesins_1.param_1 or '', table_center)
				worksheet.write('E' + str(mesin_line_1), mesins_1.param_2 or '', table_center)
				worksheet.write('F' + str(mesin_line_1), mesins_1.param_3 or '', table_center)
				worksheet.write('G' + str(mesin_line_1), mesins_1.param_4 or '', table_center)
				worksheet.write('H' + str(mesin_line_1), mesins_1.param_5 or '', table_center)
				worksheet.write('I' + str(mesin_line_1), mesins_1.param_6 or '', table_center)
				worksheet.write('J' + str(mesin_line_1), mesins_1.param_7 or '', table_center)
				worksheet.write('K' + str(mesin_line_1), mesins_1.param_8 or '', table_center)
				worksheet.write('L' + str(mesin_line_1), mesins_1.param_9 or '', table_center)
				worksheet.write('M' + str(mesin_line_1), mesins_1.param_10 or '', table_center)
				worksheet.write('N' + str(mesin_line_1), mesins_1.param_11 or '', table_center)
				worksheet.write('O' + str(mesin_line_1), mesins_1.param_12 or '', table_center)
				worksheet.write('P' + str(mesin_line_1), mesins_1.param_13 or '', table_center)
				worksheet.write('Q' + str(mesin_line_1), mesins_1.param_14 or '', table_center)
				mesin_line_1 += 1
			worksheet.merge_range('R' + str(pro_1+1) + ':U' + str(mesin_line_1-1), obj.parameter_mesin_notes or '', company_format)
			
			prod = mesin_line_1 +1
			worksheet.merge_range('A' + str(prod) + ':U' + str(prod), 'PARAMETER PRODUKSI (Pencatatan dilakukan 1 jam sekali)', table_center)
			pro_1 = prod+1
			worksheet.merge_range('A' + str(pro_1) + ':C' + str(pro_1), 'Parameter ' + str(obj.batch_1 or ''), table_center)
			worksheet.merge_range('D' + str(pro_1) + ':E' + str(pro_1), '5', table_center)
			worksheet.merge_range('F' + str(pro_1) + ':G' + str(pro_1), '6', table_center)
			worksheet.merge_range('H' + str(pro_1) + ':I' + str(pro_1), '7', table_center)
			worksheet.merge_range('J' + str(pro_1) + ':K' + str(pro_1), '8', table_center)
			worksheet.merge_range('L' + str(pro_1) + ':M' + str(pro_1), '9', table_center)
			worksheet.merge_range('N' + str(pro_1) + ':O' + str(pro_1), '10', table_center)
			worksheet.merge_range('P' + str(pro_1) + ':Q' + str(pro_1), '11', table_center)
			worksheet.merge_range('R' + str(pro_1) + ':S' + str(pro_1), '12', table_center)
			worksheet.merge_range('T' + str(pro_1) + ':U' + str(pro_1), 'Notes', table_center)
			pro_line_1 = pro_1+1
			for prods_1 in obj.prod_rec_1_line:
				worksheet.merge_range('A' + str(pro_line_1) + ':C' + str(pro_line_1), prods_1.name, table_left)
				worksheet.merge_range('D' + str(pro_line_1) + ':E' + str(pro_line_1), prods_1.param_5 or '', table_center)
				worksheet.merge_range('F' + str(pro_line_1) + ':G' + str(pro_line_1), prods_1.param_6 or '', table_center)
				worksheet.merge_range('H' + str(pro_line_1) + ':I' + str(pro_line_1), prods_1.param_7 or '', table_center)
				worksheet.merge_range('J' + str(pro_line_1) + ':K' + str(pro_line_1), prods_1.param_8 or '', table_center)
				worksheet.merge_range('L' + str(pro_line_1) + ':M' + str(pro_line_1), prods_1.param_9 or '', table_center)
				worksheet.merge_range('N' + str(pro_line_1) + ':O' + str(pro_line_1), prods_1.param_10 or '', table_center)
				worksheet.merge_range('R' + str(pro_line_1) + ':S' + str(pro_line_1), prods_1.param_11 or '', table_center)
				worksheet.merge_range('P' + str(pro_line_1) + ':Q' + str(pro_line_1), prods_1.param_12 or '', table_center)
				pro_line_1 += 1
			worksheet.merge_range('T' + str(pro_1+1) + ':U' + str(pro_line_1-1), obj.batch_note_1 or '', company_format)

			# if obj.prod_rec_2_line:
			pro_2 = pro_line_1+1
			worksheet.merge_range('A' + str(pro_2) + ':C' + str(pro_2), 'Parameter ' + str(obj.batch_2 or ''), table_center)
			worksheet.merge_range('D' + str(pro_2) + ':E' + str(pro_2), '13', table_center)
			worksheet.merge_range('F' + str(pro_2) + ':G' + str(pro_2), '14', table_center)
			worksheet.merge_range('H' + str(pro_2) + ':I' + str(pro_2), '15', table_center)
			worksheet.merge_range('J' + str(pro_2) + ':K' + str(pro_2), '16', table_center)
			worksheet.merge_range('L' + str(pro_2) + ':M' + str(pro_2), '17', table_center)
			worksheet.merge_range('N' + str(pro_2) + ':O' + str(pro_2), '18', table_center)
			worksheet.merge_range('P' + str(pro_2) + ':Q' + str(pro_2), '19', table_center)
			worksheet.merge_range('R' + str(pro_2) + ':S' + str(pro_2), '20', table_center)
			worksheet.merge_range('T' + str(pro_2) + ':U' + str(pro_2), 'Notes', table_center)
			pro_line_2 = pro_2+1
			for prods_2 in obj.prod_rec_2_line:
				worksheet.merge_range('A' + str(pro_line_2) + ':C' + str(pro_line_2), prods_2.name, table_left)
				worksheet.merge_range('D' + str(pro_line_2) + ':E' + str(pro_line_2), prods_2.param_13 or '', table_center)
				worksheet.merge_range('F' + str(pro_line_2) + ':G' + str(pro_line_2), prods_2.param_14 or '', table_center)
				worksheet.merge_range('H' + str(pro_line_2) + ':I' + str(pro_line_2), prods_2.param_15 or '', table_center)
				worksheet.merge_range('J' + str(pro_line_2) + ':K' + str(pro_line_2), prods_2.param_16 or '', table_center)
				worksheet.merge_range('L' + str(pro_line_2) + ':M' + str(pro_line_2), prods_2.param_17 or '', table_center)
				worksheet.merge_range('N' + str(pro_line_2) + ':O' + str(pro_line_2), prods_2.param_18 or '', table_center)
				worksheet.merge_range('P' + str(pro_line_2) + ':Q' + str(pro_line_2), prods_2.param_19 or '', table_center)
				worksheet.merge_range('R' + str(pro_line_2) + ':S' + str(pro_line_2), prods_2.param_20 or '', table_center)
				pro_line_2 += 1
			worksheet.merge_range('T' + str(pro_2+1) + ':U' + str(pro_line_2-1), obj.batch_note_2 or '', company_format)

			# if obj.prod_rec_3_line:
			pro_3 = pro_line_2+1
			worksheet.merge_range('A' + str(pro_3) + ':C' + str(pro_3), 'Parameter ' + str(obj.batch_3 or ''), table_center)
			worksheet.merge_range('D' + str(pro_3) + ':E' + str(pro_3), '21', table_center)
			worksheet.merge_range('F' + str(pro_3) + ':G' + str(pro_3), '22', table_center)
			worksheet.merge_range('H' + str(pro_3) + ':I' + str(pro_3), '23', table_center)
			worksheet.merge_range('J' + str(pro_3) + ':K' + str(pro_3), '24', table_center)
			worksheet.merge_range('L' + str(pro_3) + ':M' + str(pro_3), '1', table_center)
			worksheet.merge_range('N' + str(pro_3) + ':O' + str(pro_3), '2', table_center)
			worksheet.merge_range('P' + str(pro_3) + ':Q' + str(pro_3), '3', table_center)
			worksheet.merge_range('R' + str(pro_3) + ':S' + str(pro_3), '4', table_center)
			worksheet.merge_range('T' + str(pro_3) + ':U' + str(pro_3), 'Notes', table_center)
			pro_line_3 = pro_3+1
			for prods_3 in obj.prod_rec_3_line:
				worksheet.merge_range('A' + str(pro_line_3) + ':C' + str(pro_line_3), prods_3.name, table_left)
				worksheet.merge_range('D' + str(pro_line_3) + ':E' + str(pro_line_3), prods_3.param_21 or '', table_center)
				worksheet.merge_range('F' + str(pro_line_3) + ':G' + str(pro_line_3), prods_3.param_22 or '', table_center)
				worksheet.merge_range('H' + str(pro_line_3) + ':I' + str(pro_line_3), prods_3.param_23 or '', table_center)
				worksheet.merge_range('J' + str(pro_line_3) + ':K' + str(pro_line_3), prods_3.param_24 or '', table_center)
				worksheet.merge_range('L' + str(pro_line_3) + ':M' + str(pro_line_3), prods_3.param_1 or '', table_center)
				worksheet.merge_range('N' + str(pro_line_3) + ':O' + str(pro_line_3), prods_3.param_2 or '', table_center)
				worksheet.merge_range('P' + str(pro_line_3) + ':Q' + str(pro_line_3), prods_3.param_3 or '', table_center)
				worksheet.merge_range('R' + str(pro_line_3) + ':S' + str(pro_line_3), prods_3.param_4 or '', table_center)
				pro_line_3 += 1
			worksheet.merge_range('T' + str(pro_3+1) + ':U' + str(pro_line_3-1), obj.batch_note_3 or '', company_format)
	
			# bigger = sorted([pro_line_1, pro_line_2 if obj.prod_rec_2_line else 0, pro_line_3 if obj.prod_rec_3_line else 0, pro_line_4 if obj.prod_rec_4_line else 0])
			ma = pro_line_3 +1

			worksheet.merge_range('A' + str(ma) + ':T' + str(ma), 'PARAMETER PRODUCTION 2', company_format)
			worksheet.merge_range('A' + str(ma+1) + ':Q' + str(ma+1), 'LABEL USAGE', company_format)
			worksheet.write('A' + str(ma+2), 'Time Change', table_center)
			worksheet.merge_range('B' + str(ma+2) + ':C' + str(ma+2), 'Lot', table_center)
			worksheet.write('D' + str(ma+2), 'First Stock - Kg', table_center)
			worksheet.write('E' + str(ma+2), 'Start', table_center)
			worksheet.write('F' + str(ma+2), 'Finish', table_center)
			worksheet.write('G' + str(ma+2), 'In Minute', table_center)
			worksheet.write('H' + str(ma+2), 'Code Batch', table_center)
			worksheet.write('I' + str(ma+2), 'Reject', table_center)
			worksheet.write('J' + str(ma+2), 'Last Stock', table_center)
			worksheet.write('K' + str(ma+2), 'Return', table_center)
			worksheet.merge_range('L' + str(ma+2) + ':M' + str(ma+2), 'supplier Splice - Join', table_center)
			worksheet.merge_range('N' + str(ma+2) + ':O' + str(ma+2), 'supplier Splice - Actual', table_center)
			worksheet.merge_range('P' + str(ma+2) + ':Q' + str(ma+2), 'KAMI Splice', table_center)
			worksheet.merge_range('R' + str(ma+1) + ':T' + str(ma+1), 'Notes', table_center)

			tot_reject=0; tot_last_stock=0; tot_return=0; tot_join = 0; tot_actual = 0; tot_splice = 0;
			prod_line = ma +3
			for prod_2 in obj.material_line:
				tc = '%02d:%02d' % (int(prod_2.time_change), prod_2.time_change % 1 * 60) or ''
				start = '%02d:%02d' % (int(prod_2.start), prod_2.start % 1 * 60) or ''
				finish = '%02d:%02d' % (int(prod_2.finish), prod_2.finish % 1 * 60) or ''
				minute = '%02d:%02d' % (int(prod_2.in_qty), prod_2.in_qty % 1 * 60) or ''
				worksheet.write('A' + str(prod_line), tc, table_center)
				worksheet.merge_range('B' + str(prod_line) + ':C' + str(prod_line), prod_2.lot_id.name or '', table_center)
				worksheet.write('D' + str(prod_line), prod_2.fs_kg, table_center)
				worksheet.write('E' + str(prod_line), start, table_center)
				worksheet.write('F' + str(prod_line), finish, table_center)
				worksheet.write('G' + str(prod_line), minute, table_center)
				worksheet.write('H' + str(prod_line), prod_2.batch_code or '', table_center)
				worksheet.write('I' + str(prod_line), prod_2.reject_machine_qty, table_center)
				worksheet.write('J' + str(prod_line), prod_2.last_stock, table_center)
				worksheet.write('K' + str(prod_line), prod_2.return_qty, table_center)
				worksheet.merge_range('L' + str(prod_line) + ':M' + str(prod_line), prod_2.ss_join, table_center)
				worksheet.merge_range('N' + str(prod_line) + ':O' + str(prod_line), prod_2.ss_actual, table_center)
				worksheet.merge_range('P' + str(prod_line) + ':Q' + str(prod_line), prod_2.kmi_slice, table_center)
				tot_reject+=prod_2.reject_machine_qty; tot_last_stock+=prod_2.last_stock; tot_return+=prod_2.return_qty;\
				 tot_join += prod_2.ss_join; tot_actual += prod_2.ss_actual;tot_splice += prod_2.kmi_slice;
				prod_line += 1
			# prod_line +=1
			worksheet.merge_range('A' + str(prod_line) + ':H' + str(prod_line), 'Jumlah', table_center)
			worksheet.write('I' + str(prod_line), tot_reject, table_center)
			worksheet.write('J' + str(prod_line), tot_last_stock, table_center)
			worksheet.write('K' + str(prod_line), tot_return, table_center)
			worksheet.merge_range('L' + str(prod_line) + ':M' + str(prod_line), tot_join, table_center)
			worksheet.merge_range('N' + str(prod_line) + ':O' + str(prod_line), tot_actual, table_center)
			worksheet.merge_range('P' + str(prod_line) + ':Q' + str(prod_line), tot_splice, table_center)

			konv = prod_line +2
			worksheet.merge_range('A' + str(konv) + ':Q' + str(konv), 'Konversi reject label ke roll', company_format)
			worksheet.merge_range('A' + str(konv+1) + ':C' + str(konv+1) , 'Product', table_center)
			worksheet.write('D' + str(konv+1), 'Reject pcs', table_center)
			worksheet.write('E' + str(konv+1), 'Reject cm', table_center)
			worksheet.write('F' + str(konv+1), 'm (Reject pcs)', table_center)
			worksheet.write('G' + str(konv+1), 'm (Reject cm)', table_center)
			worksheet.write('H' + str(konv+1), 'Std pcs (m)', table_center)
			worksheet.write('I' + str(konv+1), 'Std cm (m)', table_center)
			worksheet.write('J' + str(konv+1), 'Reject pcs', table_center)
			worksheet.write('K' + str(konv+1), 'Reject cm', table_center)
			worksheet.write('L' + str(konv+1), 'Total Reject', table_center)
			konv_line = konv+2
			for label in obj.conversion_line:
				worksheet.merge_range('A' + str(konv_line) + ':C' + str(konv_line) , label.product_type, table_center)
				worksheet.write('D' + str(konv_line), label.reject_pcs, table_center)
				worksheet.write('E' + str(konv_line), label.reject_cm, table_center)
				worksheet.write('F' + str(konv_line), label.reject_pcs_m, table_center)
				worksheet.write('G' + str(konv_line), label.reject_cm_m, table_center)
				worksheet.write('H' + str(konv_line), label.std_pcs, table_center)
				worksheet.write('I' + str(konv_line), label.std_cm, table_center)
				worksheet.write('J' + str(konv_line), label.reject_rpcs, table_center)
				worksheet.write('K' + str(konv_line), label.reject_rcm, table_center)
				worksheet.write('L' + str(konv_line), label.total_reject, table_center)
				konv_line+=1
			worksheet.merge_range('M' + str(konv+1) + ':Q' + str(konv_line-1), '', company_format)
			worksheet.merge_range('R' + str(ma+2) + ':T' + str(konv_line-1), obj.material_usage_note or '', company_format)

			ma = konv_line + 1
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
			worksheet.merge_range('A' + str(note_row+1) + ':J' + str(note_row+5), obj.labeling_note, company_format)
			worksheet.merge_range('K' + str(note_row+1) + ':N' + str(note_row+4), '', table_header)
			worksheet.merge_range('K' + str(note_row+5) + ':N' + str(note_row+5), 'Operator: '+ obj.operator, table_header)
			worksheet.merge_range('O' + str(note_row+1) + ':R' + str(note_row+4), '', table_header)
			worksheet.merge_range('O' + str(note_row+5) + ':R' + str(note_row+5), 'Shift leader/Supervisor: '+ obj.leader, table_header)

