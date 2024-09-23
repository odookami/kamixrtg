# -*- coding: utf-8 -*-

from odoo import models
import time
import itertools
import xlsxwriter


class PartnerXlsx(models.AbstractModel):
    _name = 'report.bmo_report_bpb.usulan_pemusnaan_produk_reject_xlsx'
    _description = 'Usulan Pemusnaan Produk Reject Report'
    _inherit = 'report.report_xlsx.abstract'


    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            customer_data = ''
            company_format = workbook.add_format(
                {'bg_color': 'black', 'align': 'center', 'font_size': 25,
                    'font_color': 'white'})
            order_format = workbook.add_format(
                {'bg_color': 'black', 'align': 'center', 'font_size': 14,
                    'font_color': 'white', 'border': 1})
            table_header_left = workbook.add_format(
                {'bg_color': 'black', 'align': 'center', 'font_size': 12,
                    'font_color': 'white'})
            table_row_left = workbook.add_format(
                {'align': 'left', 'font_size': 12, 'border': 1})
            table_header_right = workbook.add_format(
                {'bg_color': 'black', 'align': 'center', 'font_size': 12,
                    'font_color': 'white', 'border': 1})
            table_row_right = workbook.add_format(
                {'align': 'center', 'font_size': 12, 'border': 1})
            customer_header_format = workbook.add_format({
                'align': 'left', 'font_size': 12, 'bold': True, 'border': 1})
            customer_format = workbook.add_format({
                'align': 'center', 'font_size': 12, 'border': 1})
            table_left = workbook.add_format(
                {'align': 'left', 'bold': True, 'border': 1})
            table_right = workbook.add_format(
                {'align': 'right', 'bold': True, 'border': 1})
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
            worksheet.merge_range('A2:F3', obj.company_id.name, company_format)
            worksheet.merge_range('A4:F4', '')
            worksheet.merge_range(
                'A5:F5', 'No FUP :- ' + obj.name, order_format)
            worksheet.merge_range('A6:F6', '')
            worksheet.merge_range(
                'A7:B7', 'Tgl Pengeluaran : ', customer_header_format)
            worksheet.merge_range(
                'C7:D7', str(obj.date_done.date()), customer_format)
            worksheet.merge_range(
                'A8:B8', 'Jenis Reject : ', customer_header_format)
            worksheet.merge_range(
                'C8:D8', obj.note, customer_format)
            worksheet.merge_range(
                'A9:B9', 'Tgl Sortir / Proses : ', customer_header_format)
            worksheet.merge_range(
                'C9:D9', str(obj.date_done.date()), customer_format)
            worksheet.merge_range('A10:F10', '')


            row = 11
            worksheet.set_column('A:A', 15)
            worksheet.set_column('B:B', 15)
            worksheet.set_column('C:C', 15)
            worksheet.set_column('D:D', 15)
            worksheet.set_column('E:E', 15)
            worksheet.set_column('F:F', 15)

            worksheet.write(row, 0, 'Product', table_header_left)
            worksheet.write(row, 1, 'Item Code', table_header_right)
            worksheet.write(row, 2, 'Kode Produksi', table_header_right)
            worksheet.write(row, 3, 'No. Palet', table_header_right)
            worksheet.write(row, 4, 'UOM', table_header_right)
            worksheet.write(row, 5, 'QTY', table_header_right)

            total_qty = 0
            for line in obj.move_line_ids_without_package:
                row += 1
                worksheet.write(row, 0, line.product_id.name, table_row_left)
                worksheet.write(row, 1, line.product_id.default_code, table_row_left)
                worksheet.write(row, 2, line.lot_id.name, table_row_left)
                worksheet.write(row, 3, line.location_id.display_name, table_row_left)
                worksheet.write(row, 4, line.product_id.uom_id.name, table_row_left)
                worksheet.write(row, 5, line.qty_done, table_row_left)
                total_qty += line.qty_done
            print(str(total_qty))
            
            row += 1
            worksheet.merge_range('A' + str(row+1) + ':E' + str(row+1), 'Total', table_row_right)
            worksheet.write(row, 5, total_qty, table_row_left)

            row += 2
            worksheet.merge_range('A' + str(row+1) + ':C' + str(row+1), 'Produksi', table_row_right)
            worksheet.merge_range('D' + str(row+1) + ':E' + str(row+1), 'Warehouse', table_row_right)

            row += 1
            worksheet.write(row, 0, 'Dibuat Oleh', table_row_right)
            worksheet.write(row, 1, 'Disetujui Oleh', table_row_right)
            worksheet.write(row, 2, 'Diserahkan Oleh', table_row_right)
            worksheet.write(row, 3, 'Disetujui Oleh', table_row_right)
            worksheet.write(row, 4, 'Diserahkan Oleh', table_row_right)

            row += 1
            worksheet.merge_range('A' + str(row+1) + ':A' + str(row+5), '', table_row_right)
            worksheet.merge_range('B' + str(row+1) + ':B' + str(row+5), '', table_row_right)
            worksheet.merge_range('C' + str(row+1) + ':C' + str(row+5), '', table_row_right)
            worksheet.merge_range('D' + str(row+1) + ':D' + str(row+5), '', table_row_right)
            worksheet.merge_range('E' + str(row+1) + ':E' + str(row+5), '', table_row_right)

            row += 5
            worksheet.write(row, 0, 'Tgl :', table_row_left)
            worksheet.write(row, 1, 'Tgl :', table_row_left)
            worksheet.write(row, 2, 'Tgl :', table_row_left)
            worksheet.write(row, 3, 'Tgl :', table_row_left)
            worksheet.write(row, 4, 'Tgl :', table_row_left)

            row += 2
            worksheet.merge_range('A' + str(row+1) + ':B' + str(row+1), 'General Afair', table_row_right)
            worksheet.merge_range('C' + str(row+1) + ':D' + str(row+1), 'Dimusnakan Oleh', table_row_right)
            worksheet.write(row, 4, 'Diketahui Oleh :', table_row_right)

            row += 1
            worksheet.write(row, 0, 'Diterima Oleh', table_row_right)
            worksheet.write(row, 1, 'Diserahkan Oleh', table_row_right)
            worksheet.write(row, 2, 'Pelaksana 1', table_row_right)
            worksheet.write(row, 3, 'Pelaksana 2', table_row_right)
            worksheet.write(row, 4, 'HRGA', table_row_right)

            row += 1
            worksheet.merge_range('A' + str(row+1) + ':A' + str(row+5), '', table_row_right)
            worksheet.merge_range('B' + str(row+1) + ':B' + str(row+5), '', table_row_right)
            worksheet.merge_range('C' + str(row+1) + ':C' + str(row+5), '', table_row_right)
            worksheet.merge_range('D' + str(row+1) + ':D' + str(row+5), '', table_row_right)
            worksheet.merge_range('E' + str(row+1) + ':E' + str(row+5), '', table_row_right)

            row += 5
            worksheet.write(row, 0, 'Tgl :', table_row_left)
            worksheet.write(row, 1, 'Tgl :', table_row_left)
            worksheet.write(row, 2, 'Tgl :', table_row_left)
            worksheet.write(row, 3, 'Tgl :', table_row_left)
            worksheet.write(row, 4, 'Tgl :', table_row_left)

            