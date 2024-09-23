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

class PackingXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_packing'
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
			worksheet.merge_range('E4:R5', 'Form Laporan Harian Packing (OBOL)', company_format)

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
			worksheet.merge_range('A11:C11', 'Total reject  produk', table_left)
			worksheet.merge_range('A12:C12', 'Total reject carton', table_left)
			worksheet.merge_range('A13:C13', 'Total output', table_left)			

			worksheet.merge_range('D8:E8', obj.preparation, table_center)
			worksheet.merge_range('D9:E9', obj.total_breakdown, table_center)
			worksheet.merge_range('D10:E10', obj.running_hours, table_center)
			worksheet.merge_range('D11:E11', obj.total_reject_produk, table_center)
			worksheet.merge_range('D12:E12', obj.total_reject_carton, table_center)
			worksheet.merge_range('D13:E13', obj.total_output, table_center)

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
			worksheet.merge_range('G12:I12', 'Start Pallet', table_left)
			worksheet.merge_range('G13:I13', 'Finish Pallet', table_left)
			c = 9
			general_line = [k for k in obj.batch_line]
			for i in general_line:
				sa = '%02d:%02d' % (int(i.start_coding), i.start_coding % 1 * 60)
				fa = '%02d:%02d' % (int(i.end_coding), i.end_coding % 1 * 60)
				worksheet.write(7, c, i.batch_number, table_center)
				worksheet.write(8, c, i.product_id.display_name, table_center)
				worksheet.write(9, c, sa, table_center)
				worksheet.write(10, c, fa, table_center)
				worksheet.write(11, c, i.start_pallet, table_center)
				worksheet.write(12, c, i.end_pallet, table_center)
				c += 1
			worksheet.merge_range('O8:Q8', 'Notes', company_format)
			worksheet.merge_range('O9:Q13', obj.note or '', company_format)
# =========================================================================================       
			worksheet.merge_range('A15:R15', 'VERIFIKASI CODING BOX (setiap ganti BO)', company_format)
			worksheet.merge_range('A16:D17', 'Setting Coding Box (oleh QC) ', table_center)
			worksheet.merge_range('E16:H17', 'Actual Coding Box (upload) ', table_center)
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
				worksheet.merge_range('K' + str(row) + ':L' + str(row), cc, table_left)
				worksheet.merge_range('M' + str(row) + ':N' + str(row), coding.pic_qc, table_center)
				worksheet.merge_range('O' + str(row) + ':P' + str(row), ca, table_center)
				worksheet.merge_range('Q' + str(row) + ':R' + str(row), coding.status_verifikasi, table_center)
				row += 1
			worksheet.merge_range('S16' + ':U'+ str(row-1), obj.note_vefiri_coding or '', table_center)
# =========================================================================================     
			check = row +1
			worksheet.merge_range('A' + str(check) + ':U' + str(check), 'GENERAL CHECKS ( early shift checks)', company_format)

			cek_1 = check+1
			worksheet.merge_range('A' + str(cek_1) + ':C' + str(cek_1), 'Invopack Parameter', table_center)
			worksheet.merge_range('D' + str(cek_1) + ':E' + str(cek_1), 'Std', table_center)
			worksheet.write('F' + str(cek_1), 'Actual', table_center)
			for check_1 in obj.checks_1_line:
				worksheet.merge_range('A' + str(cek_1+1)+':C' + str(cek_1+1), check_1.name or '', table_left)
				worksheet.merge_range('D' + str(cek_1+1)+':E' + str(cek_1+1), check_1.standard or '', table_center)
				worksheet.write('F' + str(cek_1+1), check_1.actual or '', table_center)
				cek_1 +=1
			
			cek_2 = check+1
			worksheet.merge_range('G' + str(cek_2) + ':I' + str(cek_2), 'Robotic Parameter', table_center)
			worksheet.merge_range('J' + str(cek_2) + ':K' + str(cek_2), 'Std', table_center)
			worksheet.write('L' + str(cek_2), 'Actual', table_center)
			for check_2 in obj.checks_2_line:
				worksheet.merge_range('G' + str(cek_2+1)+':I' + str(cek_2+1), check_2.name or '', table_left)
				worksheet.merge_range('J' + str(cek_2+1)+':K' + str(cek_2+1), check_2.standard or '', table_center)
				worksheet.write('L' + str(cek_2+1), check_2.actual or '', table_center)
				cek_2 +=1

			cek_3 = check+1
			worksheet.merge_range('M' + str(cek_3) + ':O' + str(cek_3), 'Glue Parameter', table_center)
			worksheet.merge_range('P' + str(cek_3) + ':Q' + str(cek_3), 'Std', table_center)
			worksheet.write('R' + str(cek_3), 'Actual', table_center)
			for check_3 in obj.checks_3_line:
				worksheet.merge_range('M' + str(cek_3+1)+':O' + str(cek_3+1), check_3.name or '', table_left)
				worksheet.merge_range('P' + str(cek_3+1)+':Q' + str(cek_3+1), check_3.standard or '', table_center)
				worksheet.write('R' + str(cek_3+1), check_3.actual or '', table_center)
				cek_3 +=1

			cek_4 = cek_1+2
			worksheet.merge_range('A' + str(cek_4) + ':C' + str(cek_4), 'Coding Parameter', table_center)
			worksheet.merge_range('D' + str(cek_4) + ':E' + str(cek_4), 'Std', table_center)
			worksheet.write('F' + str(cek_4), 'Actual', table_center)
			for check_4 in obj.checks_4_line:
				worksheet.merge_range('A' + str(cek_4+1)+':C' + str(cek_4+1), check_4.name or '', table_left)
				worksheet.merge_range('D' + str(cek_4+1)+':E' + str(cek_4+1), check_4.standard or '', table_center)
				worksheet.write('F' + str(cek_4+1), check_4.actual or '', table_center)
				cek_4 +=1
			
			cek_5 = cek_2+3
			worksheet.merge_range('G' + str(cek_5) + ':I' + str(cek_5), 'Pembalik box Parameter', table_center)
			worksheet.merge_range('J' + str(cek_5) + ':K' + str(cek_5), 'Std', table_center)
			worksheet.write('L' + str(cek_5), 'Actual', table_center)
			for check_5 in obj.checks_5_line:
				worksheet.merge_range('G' + str(cek_5+1)+':I' + str(cek_5+1), check_5.name or '', table_left)
				worksheet.merge_range('J' + str(cek_5+1)+':K' + str(cek_5+1), check_5.standard or '', table_center)
				worksheet.write('L' + str(cek_5+1), check_5.actual or '', table_center)
				cek_5 +=1
			
			cek_6 = check+1
			worksheet.merge_range('S' + str(cek_6) + ':U' + str(cek_6), 'Total Reject Product', table_center)
			worksheet.merge_range('S' + str(cek_6+1) + ':T' + str(cek_6+1), 'BO', table_center)
			worksheet.write('U' + str(cek_6+1), 'QTY', table_center)
			for re in obj.checks_6_line:
				worksheet.merge_range('S' + str(cek_6+2) + ':T' + str(cek_6+2), re.reject_bo, table_center)
				worksheet.write('U' + str(cek_6+2), re.reject_qty, table_center)
				cek_6 += 1

			note = cek_6+3
			worksheet.merge_range('S' + str(note+2) + ':U' + str(note+2), 'Notes', table_center)
			worksheet.merge_range('S' + str(note+3) + ':U' + str(note+6), obj.note_checks or '', table_center)
			
			bigger = sorted([cek_1, cek_2, cek_3, cek_4, cek_5, note])
			ma = bigger[-1]+2

			# worksheet.merge_range('A16:D17', 'Setting Coding Box (oleh QC) ', table_center)
			worksheet.merge_range('A' + str(ma) + ':T' + str(ma), 'PRODUCTION RECORD', company_format)
			worksheet.merge_range('A' + str(ma+1) + ':T' + str(ma+1), 'Material Usage', company_format)
			worksheet.merge_range('A' + str(ma+2) + ':B' + str(ma+2), 'Time Change', company_format)
			worksheet.write('C' + str(ma+2), 'Banded 6', company_format)
			worksheet.write('D' + str(ma+2), 'Single', company_format)
			worksheet.merge_range('E' + str(ma+2) + ':F' + str(ma+2), 'Lot', table_center)
			worksheet.merge_range('G' + str(ma+2) + ':H' + str(ma+2), 'In', table_center)
			worksheet.merge_range('I' + str(ma+2) + ':J' + str(ma+2), 'Out', table_center)
			worksheet.merge_range('K' + str(ma+2) + ':L' + str(ma+2), 'Sample QC', table_center)
			worksheet.merge_range('M' + str(ma+2) + ':N' + str(ma+2), 'Reject Mesin/ maanual', table_center)
			worksheet.merge_range('O' + str(ma+2) + ':P' + str(ma+2), 'Reject Coding', table_center)
			worksheet.merge_range('Q' + str(ma+2) + ':R' + str(ma+2), 'Reject Supplier', table_center)
			worksheet.merge_range('S' + str(ma+2) + ':T' + str(ma+2), 'Last Stock', table_center)

			total_in = 0; total_out = 0; total_sample = 0; tot_reject_mesin=0; tot_reject_cod=0; tot_reject_sup=0; tot_last_stock = 0
			for maseg in obj.material_line:
				tc = '%02d:%02d' % (int(maseg.time_change), maseg.time_change % 1 * 60)
				worksheet.merge_range('A' + str(ma+3) + ':B' + str(ma+3), tc , company_format)
				worksheet.write('C' + str(ma+3), maseg.material_banded_6, company_format)
				worksheet.write('D' + str(ma+3), maseg.material_single, company_format)
				worksheet.merge_range('E' + str(ma+3) + ':F' + str(ma+3), maseg.lot_id.name or '', table_center)
				worksheet.merge_range('G' + str(ma+3) + ':H' + str(ma+3), maseg.in_qty, table_center)
				worksheet.merge_range('I' + str(ma+3) + ':J' + str(ma+3), maseg.out_qty, table_center)
				worksheet.merge_range('K' + str(ma+3) + ':L' + str(ma+3), maseg.sample_qc, table_center)
				worksheet.merge_range('M' + str(ma+3) + ':N' + str(ma+3), maseg.reject_machine_qty, table_center)
				worksheet.merge_range('O' + str(ma+3) + ':P' + str(ma+3), maseg.reject_coding_qty, table_center)
				worksheet.merge_range('Q' + str(ma+3) + ':R' + str(ma+3), maseg.reject_supplier_qty, table_center)
				worksheet.merge_range('S' + str(ma+3) + ':T' + str(ma+3), maseg.last_stock, table_center)
				total_in += maseg.in_qty; total_out += maseg.out_qty; total_sample += maseg.sample_qc; tot_reject_mesin+=maseg.reject_machine_qty;\
			    tot_reject_cod+=maseg.reject_coding_qty; tot_reject_sup+=maseg.reject_supplier_qty; tot_last_stock += maseg.last_stock;
				ma += 1		
			
			ma +=3
			worksheet.merge_range('A' + str(ma) + ':F' + str(ma), 'Jumlah', table_center)
			worksheet.merge_range('G' + str(ma) + ':H' + str(ma), total_in, table_center)
			worksheet.merge_range('I' + str(ma) + ':J' + str(ma), total_out, table_center)
			worksheet.merge_range('K' + str(ma) + ':L' + str(ma), total_sample, table_center)
			worksheet.merge_range('M' + str(ma) + ':N' + str(ma), tot_reject_mesin, table_center)
			worksheet.merge_range('O' + str(ma) + ':P' + str(ma), tot_reject_cod, table_center)
			worksheet.merge_range('Q' + str(ma) + ':R' + str(ma), tot_reject_sup, table_center)
			worksheet.merge_range('S' + str(ma) + ':T' + str(ma), tot_last_stock, table_center)

			ma += 2
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
			worksheet.merge_range('A' + str(note_row+1) + ':J' + str(note_row+5), obj.packing_note, company_format)
			worksheet.merge_range('K' + str(note_row+1) + ':N' + str(note_row+4), '', table_header)
			worksheet.merge_range('K' + str(note_row+5) + ':N' + str(note_row+5), 'Operator: '+ obj.operator, table_header)
			worksheet.merge_range('O' + str(note_row+1) + ':R' + str(note_row+4), '', table_header)
			worksheet.merge_range('O' + str(note_row+5) + ':R' + str(note_row+5), 'Shift leader: '+ obj.leader, table_header)
