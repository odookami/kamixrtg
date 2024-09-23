# -*- coding: utf-8 -*-

from odoo import models
import time
import itertools
import xlsxwriter


class PartnerXlsx(models.AbstractModel):
	_name = 'report.bmo_daily_report.report_unscramble'
	_description = 'Daily Report Unscramble'
	_inherit = 'report.report_xlsx.abstract'

	def generate_xlsx_report(self, workbook, data, partners):
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

			worksheet.merge_range('A2:D5', 'PT Kalbe Milko Indonesia', company_format)
			
			worksheet.merge_range('E2:R3', 'QC DEPARTEMENT', company_format)
			worksheet.merge_range('E4:R5', 'PERMINTAAN SAMPLE', company_format)

			worksheet.merge_range('S2:U2', 'No Dok: ' + obj.name, table_left)
			worksheet.merge_range('S3:U3', 'Tanggal: ' + str(obj.date), table_left)
			worksheet.merge_range('S4:U4', 'Hal: ', table_left)
			worksheet.merge_range('S5:U5', 'Revisi: ', table_left)

			worksheet.merge_range('A7:O7', 'GENERAL REPORT', company_format)
			worksheet.merge_range('P7:U7', 'Notes', company_format)
			# KIRI
			worksheet.merge_range('A8:C8', 'Preparation', table_left)
			worksheet.merge_range('A9:C9', 'Total Breakdown', table_left)
			worksheet.merge_range('A10:C10', 'Running hours', table_left)
			worksheet.merge_range('A11:C11', 'Total reject unscramble A', table_left)
			worksheet.merge_range('A12:C12', 'Total reject unscramble B', table_left)
			worksheet.merge_range('A13:C13', 'Total reject Rinser', table_left)
			worksheet.merge_range('A14:C14', 'Speed max unscramble A', table_left)
			worksheet.merge_range('A15:C15', 'Speed max unscramble B', table_left)

			worksheet.merge_range('D8:F8', obj.preparation, table_center)
			worksheet.merge_range('D9:F9', obj.total_breakdown, table_center)
			worksheet.merge_range('D10:F10', obj.running_hours, table_center)
			worksheet.merge_range('D11:F11', obj.total_reject_unscramble_a, table_center)
			worksheet.merge_range('D12:F12', obj.total_reject_unscramble_b, table_center)
			worksheet.merge_range('D13:F13', obj.total_reject_rinser, table_center)
			worksheet.merge_range('D14:F14', obj.speed_max_unscramble_a, table_center)
			worksheet.merge_range('D15:F15', obj.speed_max_unscramble_b, table_center)

			worksheet.write('G8', 'min', table_center)
			worksheet.write('G9', 'min', table_center)
			worksheet.write('G10', 'min', table_center)
			worksheet.write('G11', 'btl', table_center)
			worksheet.write('G12', 'btl', table_center)
			worksheet.write('G13', 'btl', table_center)
			worksheet.write('G14', 'btl/min', table_center)
			worksheet.write('G15', 'btl/min', table_center)
			# KANAN
			worksheet.merge_range('H8:I8', 'Hari', table_left)
			worksheet.merge_range('H9:I9', 'Tanggal', table_left)
			worksheet.merge_range('H10:I10', 'Shift', table_left)

			worksheet.merge_range('J8:K8', obj.dayofweek, table_center)
			worksheet.merge_range('J9:K9', str(obj.date), table_center)
			worksheet.merge_range('J10:K10', obj.shift, table_center)

			worksheet.merge_range('L8:M8', 'Team', table_left)
			worksheet.merge_range('L9:M9', 'Kemasan (ml)', table_left)
			worksheet.merge_range('L10:M10', 'Line Machine', table_left)

			worksheet.merge_range('N8:O8', obj.team, table_center)
			worksheet.merge_range('N9:O9', obj.packaging, table_center)
			worksheet.merge_range('N10:O10', obj.line_machine, table_center)

			worksheet.merge_range('H11:K11', 'Product name/batch ', table_left)
			worksheet.merge_range('H12:K12', 'Start production time', table_left)
			worksheet.merge_range('H13:K13', 'Counter Rinser', table_left)

			worksheet.merge_range('L11:M11', obj.product_name_batch, table_left)
			worksheet.merge_range('L12:M12', obj.start_production_time, table_left)
			worksheet.merge_range('L13:M13', obj.counter_rinser, table_left)

			worksheet.merge_range('N11:O11', '', table_left)
			worksheet.merge_range('N12:O12', '', table_left)
			worksheet.merge_range('N13:O13', '', table_left)

			worksheet.merge_range('H14:O15', '', company_format)

			worksheet.merge_range('P8:U15', '', company_format)

			# set col width
			# worksheet.set_column('A:A', 13)
			# worksheet.set_column('B:B', 15)
			# worksheet.set_column('C:C', 35)
			# worksheet.set_column('D:D', 25)
			# worksheet.set_column('E:E', 18)
			# worksheet.set_column('F:F', 10)
			# worksheet.set_column('G:G', 15)
			# worksheet.set_column('H:H', 25)
			
			worksheet.merge_range('A17:H17', 'GENERAL CHECKS ( early shift checks)', company_format)
			
			worksheet.merge_range('A18:C18', 'Parameter', table_header)
			worksheet.merge_range('D18:E18', 'Std', table_header)
			worksheet.merge_range('F18:G18', 'Actual', table_header)

			row = 19
			for line in obj.checks_line:
				worksheet.merge_range('A' + str(row) + ':C' + str(row), line.name, table_left)
				worksheet.merge_range('D' + str(row) + ':E' + str(row), line.standard, table_center)
				worksheet.merge_range('F' + str(row) + ':G' + str(row), line.actual, table_center)
				row += 1
			
			worksheet.merge_range('J17:U17', 'PARAMETER MESIN (Pengecekan parameter)', company_format)
			row_time = 17; row_isi = 18; col = 10
			for mesin in obj.params_mch_line:
				worksheet.write(row_time, col, mesin.check_time, table_left)
				col+=1
				for isi in mesin.detail_mch_line:
					worksheet.write('J' + str(row_isi+1), isi.name, table_left)
					row_isi+=1
					

			bot_row_a = row + 2
			worksheet.merge_range('A' + str(bot_row_a) + ':J' + str(bot_row_a), 'BOTTLE RECORD SILO A', company_format)
			worksheet.merge_range('A' + str(bot_row_a+1) + ':C' + str(bot_row_a+1), 'Bottle code/name', table_header)
			worksheet.write('D' + str(bot_row_a+1), 'Lot', table_left)
			worksheet.merge_range('E' + str(bot_row_a+1) + ':F' + str(bot_row_a+1), 'Supplier', table_header)
			worksheet.write('G' + str(bot_row_a+1), 'Time', table_left)
			worksheet.write('H' + str(bot_row_a+1), 'In', table_left)
			worksheet.write('I' + str(bot_row_a+1), 'Out', table_left)
			worksheet.write('J' + str(bot_row_a+1), 'Stock Akhir', table_left)
			

			total_in_a = 0; total_out_a = 0; total_end_a = 0
			bot_row_a += 1
			for bot_a in obj.bottle_record_silo_a_ids:
				worksheet.merge_range('A' + str(bot_row_a+1) + ':C' + str(bot_row_a+1), bot_a.bottle_id.display_name, table_header)
				worksheet.write('D' + str(bot_row_a+1), bot_a.lot or '', table_left)
				worksheet.merge_range('E' + str(bot_row_a+1) + ':F' + str(bot_row_a+1), bot_a.supplier.name, table_header)
				worksheet.write('G' + str(bot_row_a+1), str(bot_a.time.date()), table_left)
				worksheet.write('H' + str(bot_row_a+1), bot_a.bottle_in, table_left)
				worksheet.write('I' + str(bot_row_a+1), bot_a.bottle_out, table_left)
				worksheet.write('J' + str(bot_row_a+1), bot_a.stock_akhir, table_left)
				total_in_a += bot_a.bottle_in; total_out_a += bot_a.bottle_out; total_end_a += bot_a.stock_akhir
				bot_row_a += 1

			bot_row_a += 1
			worksheet.merge_range('A' + str(bot_row_a) + ':G' + str(bot_row_a), 'Jumlah', table_header)
			worksheet.write('H' + str(bot_row_a), total_in_a, table_left)
			worksheet.write('I' + str(bot_row_a), total_out_a, table_left)
			worksheet.write('J' + str(bot_row_a), total_end_a, table_left)
			
			bot_row_b = row + 2
			worksheet.merge_range('L' + str(bot_row_b) + ':U' + str(bot_row_b), 'BOTTLE RECORD SILO B', company_format)
			worksheet.merge_range('L' + str(bot_row_b+1) + ':N' + str(bot_row_b+1), 'Bottle code/name', table_header)
			worksheet.write('O' + str(bot_row_b+1), 'Lot', table_left)
			worksheet.merge_range('P' + str(bot_row_b+1) + ':Q' + str(bot_row_b+1), 'Supplier', table_header)
			worksheet.write('R' + str(bot_row_b+1), 'Time', table_left)
			worksheet.write('S' + str(bot_row_b+1), 'In', table_left)
			worksheet.write('T' + str(bot_row_b+1), 'Out', table_left)
			worksheet.write('U' + str(bot_row_b+1), 'Stock Akhir', table_left)
			
			
			total_in_b = 0; total_out_b = 0; total_end_b = 0
			bot_row_b += 2
			for bot_b in obj.bottle_record_silo_b_ids:
				worksheet.merge_range('L' + str(bot_row_b) + ':N' + str(bot_row_b), bot_b.bottle_id.display_name, table_header)
				worksheet.write('O' + str(bot_row_b), bot_b.lot or '', table_left)
				worksheet.merge_range('P' + str(bot_row_b) + ':Q' + str(bot_row_b), bot_b.supplier.name, table_header)
				worksheet.write('R' + str(bot_row_b), str(bot_b.time.date()), table_left)
				worksheet.write('S' + str(bot_row_b), bot_b.bottle_in, table_left)
				worksheet.write('T' + str(bot_row_b), bot_b.bottle_out, table_left)
				worksheet.write('U' + str(bot_row_b), bot_b.stock_akhir, table_left)
				worksheet.write('U' + str(bot_row_b), bot_b.stock_akhir, table_left)
				total_in_b += bot_b.bottle_in; total_out_b += bot_b.bottle_out; total_end_b += bot_b.stock_akhir
				bot_row_b += 1
			
			# bot_row_b +=1
			worksheet.merge_range('L' + str(bot_row_b) + ':R' + str(bot_row_b), 'Jumlah', table_header)
			worksheet.write('S' + str(bot_row_b), total_in_b, table_left)
			worksheet.write('T' + str(bot_row_b), total_out_b, table_left)
			worksheet.write('U' + str(bot_row_b), total_end_b, table_left)

			note_row = bot_row_b +1
			worksheet.merge_range('A' + str(note_row+1) + ':J' + str(note_row+5), obj.unscramble_note, company_format)
			worksheet.merge_range('K' + str(note_row+1) + ':M' + str(note_row+4), '', table_header)
			worksheet.merge_range('K' + str(note_row+5) + ':M' + str(note_row+5), 'Operator ', table_header)
			worksheet.merge_range('N' + str(note_row+1) + ':P' + str(note_row+4), '', table_header)
			worksheet.merge_range('N' + str(note_row+5) + ':P' + str(note_row+5), 'Shift leader', table_header)
			worksheet.merge_range('Q' + str(note_row+1) + ':S' + str(note_row+4), '', table_header)
			worksheet.merge_range('Q' + str(note_row+5) + ':S' + str(note_row+5), 'SPV/Manager', table_header)
