# -*- coding: utf-8 -*-

from odoo import models
import time
import itertools
import xlsxwriter


class PartnerXlsx(models.AbstractModel):
	_name = 'report.bmo_inventory_qc.qc_sample_request'
	_description = 'QC Sample Request'
	_inherit = 'report.report_xlsx.abstract'


	def generate_xlsx_report(self, workbook, data, partners):
		for obj in partners:
			customer_data = ''
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

			if obj.partner_id.name:
				customer_data += obj.partner_id.name + '\n'
			if obj.partner_id.street:
				customer_data += obj.partner_id.street + '\n'
			if obj.partner_id.street2:
				customer_data += obj.partner_id.street2 + '\n'
			if obj.partner_id.city:
				customer_data += obj.partner_id.city + ' '
			if obj.partner_id.state_id:
				customer_data += str(obj.partner_id.state_id.name + ' ')
			if obj.partner_id.zip:
				customer_data += obj.partner_id.zip + ' '
			if obj.partner_id.country_id:
				customer_data += '\n' + str(obj.partner_id.country_id.name)

			worksheet = workbook.add_worksheet(obj.name)

			worksheet.merge_range('A2:C5', obj.company_id.name, company_format)
			
			worksheet.merge_range('D2:H2', 'QC DEPARTEMENT', company_format)
			worksheet.merge_range('D3:H4', 'PERMINTAAN SAMPLE', company_format)
			worksheet.merge_range('D5:H5', '                            No: ', table_left)

			worksheet.merge_range('I2:K2', 'No Dok: ' + obj.name, table_left)
			worksheet.merge_range('I3:K3', 'Tanggal: ' + str(obj.scheduled_date.date()), table_left)
			worksheet.merge_range('I4:K4', 'Hal: ', table_left)
			worksheet.merge_range('I5:K5', 'Revisi: ', table_left)

			worksheet.write(6, 0, 'From', table_left)
			worksheet.merge_range('B7:C7', '', table_left)
			
			worksheet.write(7, 0, 'Date', table_left)
			worksheet.merge_range('B8:C8', '', table_left)

			worksheet.write(6, 4, 'To', table_left)
			worksheet.merge_range('F7:G7', '', table_left)

			row = 11
			worksheet.set_column('A:A', 13)
			worksheet.set_column('B:B', 15)
			worksheet.set_column('C:C', 35)
			worksheet.set_column('D:D', 25)
			worksheet.set_column('E:E', 18)
			worksheet.set_column('F:F', 10)
			worksheet.set_column('G:G', 15)
			worksheet.set_column('H:H', 25)

			worksheet.write(row, 0, 'No', table_header)
			worksheet.write(row, 1, 'Item Code', table_header)
			worksheet.write(row, 2, 'Item Desccription', table_header)
			worksheet.write(row, 3, 'LOT', table_header)
			worksheet.write(row, 4, 'ED', table_header)
			worksheet.write(row, 5, 'QTY', table_header)
			worksheet.write(row, 6, 'UOM', table_header)
			worksheet.write(row, 7, 'Keterangan', table_header)

			no = 1
			for line in obj.move_line_ids_without_package:
				row += 1
				date = str(line.expired_date.date()) if line.expired_date else ''

				worksheet.write(row, 0, no, table_row_left)
				worksheet.write(row, 1, line.product_id.default_code, table_row_left)
				worksheet.write(row, 2, line.product_id.name, table_row_left)
				worksheet.write(row, 3, line.lot_id.name or '', table_row_left)
				worksheet.write(row, 4, date, table_row_left)
				worksheet.write(row, 5, line.qty_done, table_row_left)
				worksheet.write(row, 6, line.product_uom_id.name, table_row_left)
				worksheet.write(row, 7, '', table_row_left)
				no +=1

			row += 3
			worksheet.merge_range('A' + str(row+1) + ':B' + str(row+1), 'Notes:', table_row_right)
			worksheet.write(row, 2, 'Dibuat Oleh', table_row_right)
			worksheet.write(row, 3, 'Disetujui Oleh', table_row_right)
			worksheet.write(row, 4, 'Diserahkan Oleh', table_row_right)

			row += 1
			worksheet.merge_range('A' + str(row+1) + ':B' + str(row+5), obj.note or '', table_row_right)
			worksheet.merge_range('C' + str(row+1) + ':C' + str(row+5), '', table_row_right)
			worksheet.merge_range('D' + str(row+1) + ':D' + str(row+5), '', table_row_right)
			worksheet.merge_range('E' + str(row+1) + ':E' + str(row+5), '', table_row_right)

