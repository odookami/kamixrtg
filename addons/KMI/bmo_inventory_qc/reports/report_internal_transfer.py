from os import stat
import re
import xlwt
import base64, io
import itertools
from PIL import Image
from io import StringIO, BytesIO
from odoo import api, fields, models, _
from datetime import date, datetime, timedelta
import platform

class InternalTransferReport(models.TransientModel):        
	_name = 'internal.transfer.report'
	_description = 'Internal Transfer Report'
	
	picking_data = fields.Char('Name', size=256)
	file_name = fields.Binary('Internal Transfer Report', readonly=True)
	
class WizardWizards(models.TransientModel):        
	_name = 'wizard.reports'
	_description = 'IT wizard'
	
	# @api.multi
	def action_picking_report(self):          
		custom_value = {}
		picking = self.env['stock.picking'].browse(self._context.get('active_ids', list())) 
		reason_qc_temp = self.env['inventory.quality.check.template'].search([])
		workbook = xlwt.Workbook()
		for rec in picking:
			qce = []

			for detop in rec.move_line_nosuggest_ids:
				expiry= detop.expiration_date.strftime("%Y-%m-%d") if detop.expiration_date else ''

			for qc in rec.stock_move_quality_check_line:
				check = {}

				data = dict(qc.fields_get(['status_qc'])['status_qc']['selection'])
				if qc.production_date:
					production_date = qc.production_date.strftime("%Y-%m-%d")
				else:
					production_date = ''

				check ['product_id_code'] = qc.product_id.default_code
				check ['product_id_name'] = qc.product_id.name
				check ['lot_number'] = qc.lot_id.name if qc.lot_id else ''  
				check ['manufacturer_plant'] = qc.manufacturer_plant.name or ''
				check ['origin'] = qc.origin.name or ''
				check ['qty_done'] = qc.qty
				check ['product_uom'] = qc.product_id.uom_id.name
				check ['date_prod'] = production_date
				# check ['date_expry'] = qc.lot_id.expiration_date.strftime("%Y-%m-%d") if qc.lot_id.expiration_date else '',
				check ['status'] = [] 
				check ['status_qc'] = [v for k,v in data.items() if k == qc.status_qc ][0]
				check ['note_qc'] = qc.reject_reason or ''

				for lines in qc.quality_check_line:
					if lines:
						status = lines.parameter_text
					else:
						status = ''
					check ['status'].append(status)

				qce.append(check)
	
			# qty_done = [int(opdet.qty_done) for opdet in rec.move_line_nosuggest_ids]
																						   
			custom_value['quality_check'] = qce
			custom_value ['reference'] = rec.name   
			custom_value ['scheduled_date'] = rec.scheduled_date.strftime("%Y-%m-%d") or ''
			custom_value ['efective_date'] = rec.date_done.strftime("%Y-%m-%d") if rec.date_done else  ''
			custom_value ['source_document'] = rec.origin or ''
			custom_value ['note'] = rec.note or '' 
			custom_value ['date_expry'] = expiry
												  
			style0 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz right;', num_format_str='#,##0.00')
			style1 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz center;', num_format_str='#,##0.00')
			style2 = xlwt.easyxf('font:height 400,bold True;borders:left thin, right thin, top thin, bottom thin;', num_format_str='#,##0.00')
			style3 = xlwt.easyxf('font:bold True;borders:left thin, right thin, top thin, bottom thin;', num_format_str='#,##0.00')
			style4 = xlwt.easyxf('font:bold True;  borders:top double,right thin;align: horiz right;', num_format_str='#,##0.00')
			style5 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz center;', num_format_str='#,##0')
			style6 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;', num_format_str='#,##0.00')
			style7 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')
			style8 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin, right thin, top thin, bottom thin;align: horiz right;', num_format_str='DD-MM-YYYY')
			style3_1 = xlwt.easyxf('font: name Times New Roman bold on;borders:left thin;align: horiz right;', num_format_str='#,##0.00')
			style4_1 = xlwt.easyxf('borders:top thin;', num_format_str='#,##0.00')
			style5_1 = xlwt.easyxf('borders:left thin;', num_format_str='#,##0.00')
			style6_1 = xlwt.easyxf('font:bold True;  borders:top double;', num_format_str='#,##0.00')
			style7_1 = xlwt.easyxf('borders:left thin,bottom thin,right thin;', num_format_str='#,##0.00')
			style10 = xlwt.easyxf('font: name Times New Roman bold on;borders:left medium, right medium, top medium, bottom medium;align: vert center, horiz center;', num_format_str='#,##0.00')
			style11 = xlwt.easyxf('font: name Times New Roman bold on;borders:left medium, right medium, top medium, bottom medium;', num_format_str='#,##0.00')
			style12 = xlwt.easyxf('font: name Times New Roman bold on;borders:left medium, right medium, top medium, bottom medium;align: horiz right;', num_format_str='#,##0.00')
			style13 = xlwt.easyxf('font: name Times New Roman bold on;borders:left medium, right medium, top medium, bottom medium;align: horiz left;', num_format_str='#,##0.00')

			style1_1 = xlwt.easyxf('borders:top medium;')
			style1_2 = xlwt.easyxf('borders:top medium,right medium;')
			style1_3 = xlwt.easyxf('borders:right medium;')
			style13_1 = xlwt.easyxf('font: name Times New Roman bold on;borders:top medium;align: horiz left;', num_format_str='#,##0.00')
			style13_2 = xlwt.easyxf('font: name Times New Roman bold on;align: horiz left;', num_format_str='#,##0.00')
			sheet = workbook.add_sheet(rec.name)

			sheet.write_merge(1, 2, 4, 15, 'Quality Control Department', style10)
			sheet.write_merge(3, 4, 4, 15, 'Form Pengecekan Fisik Raw Material dan Packaging Material', style10)

			# box kiri atas
			sheet.write_merge(1, 4, 1, 3, rec.company_id.name, style10)

			# style box kanan atas
			sheet.write(1, 17, '', style1_1)
			sheet.write(1, 19, '', style1_1)
			sheet.write_merge(1, 1, 20, 21, '', style1_1)
			sheet.write(1, 22, '', style1_2)
			sheet.write(2, 22, '', style1_3)
			sheet.write(3, 22, '', style1_3)
			sheet.write(4, 22, '', style1_3)

			# isi box kanan atas
			sheet.write(1, 16, 'No. Dokumen', style13_1)
			sheet.write(1, 18, ': '+ custom_value['reference'], style13_1)
			sheet.write(2, 16, 'Tanggal', style13_2)
			sheet.write(2, 18, ': '+custom_value['scheduled_date'], style13_2)
			sheet.write(3, 16, 'Halaman', style13_2)
			sheet.write(3, 18, ': ', style13_2)
			sheet.write(4, 16, 'Revisi', style13_2)
			sheet.write(4, 18, ': ', style13_2)
			
			# sheet.write_merge(9, 10, 1, 1, 'NO', style1)        
			sheet.write_merge(5, 5, 1, 2, 'Tanggal', style10)        
			sheet.write(6, 1, 'Kedatangan', style10)
			sheet.write(6, 2, 'Pengecekan', style10)
			sheet.write_merge(5, 6, 3, 3, 'DO Number', style10)
			sheet.write_merge(5, 6, 4, 4, 'Item Code', style10)
			sheet.write_merge(5, 6, 5, 5, 'Item Description', style10)
			sheet.write_merge(5, 6, 6, 6, 'LOT NUMBER', style10)
			sheet.write_merge(5, 6, 7, 7, 'Manufacturer Plant', style10)  
			sheet.write_merge(5, 6, 8, 8, 'Counrty Of Origin', style10)      
			sheet.write_merge(5, 6, 9, 9, 'Quantity', style10)
			sheet.write_merge(5, 6, 10, 10, 'UOM', style10)
			sheet.write_merge(5, 5, 11, 12, 'Date', style10)
			sheet.write(6, 11, 'Production', style10)
			sheet.write(6, 12, 'Expired', style10)
			c = 13
			for i in reason_qc_temp:
				# sheet.write_merge(5, 5, 13, c, 'Document', style10)
				# sheet.write_merge(5, 5, c, c, 'Kondisi', style10)
				sheet.write_merge(5, 6, c, c, i.name, style10)
				c += 1
			sheet.write_merge(5, 6, c, c, 'Status', style10)
			sheet.write_merge(5, 6, c+1, c+1, 'Note', style10)
			# sheet.write(6, 13, 'CoA/RoA', style10)
			# sheet.write(6, 14, 'ASL', style10)
			# sheet.write(6, 15, 'Bocor', style10)
			# sheet.write(6, 16, 'Rusak', style10)
			# sheet.write(6, 17, 'Kotor', style10)
			# sheet.write(6, 18, 'Basah', style10)
			# sheet.write(6, 19, 'Pest', style10)

			n = 7; m=6; i = 1

			for check in custom_value['quality_check']:
				# print('==================================',product)
				
				# sheet.write(n, 1, i, style5)  
				sheet.write(n, 1, custom_value['scheduled_date'], style11) 
				sheet.write(n, 2, custom_value['efective_date'], style11) 
				sheet.write(n, 3, custom_value['source_document'], style11) 
				sheet.write(n, 4, check['product_id_code'], style11)
				sheet.write(n, 5, check['product_id_name'], style11)            
				sheet.write(n, 6, check['lot_number'], style12)
				sheet.write(n, 7, check['manufacturer_plant'], style12) 
				sheet.write(n, 8, check['origin'], style12)
				sheet.write(n, 9, check['qty_done'], style12)
				sheet.write(n, 10, check['product_uom'], style12)
				sheet.write(n, 11, check ['date_prod'], style12)
				sheet.write(n, 12, custom_value['date_expry'], style12)
				
				r = n; c = 13
				for cek in check['status']:
					sheet.write(r, c, cek, style12)
					c += 1
				sheet.write(r, c, check['status_qc'], style12)
				sheet.write(r, c+1, check['note_qc'], style12)
				# sheet.write(n, 13, check['status'][0], style12)
				# sheet.write(n, 14, check['status'][1], style12)
				# sheet.write(n, 15, check['status'][2], style12)
				# sheet.write(n, 16, check['status'][3], style12)
				# sheet.write(n, 17, check['status'][4], style12)
				# sheet.write(n, 18, check['status'][5], style12)
				# sheet.write(n, 19, check['status'][6], style12)

				n += 1; m +=1; i += 1
			
			sheet.write_merge(n+8, n+8, 1, 10, 'note:', style11)
			sheet.write_merge(n+9, n+12, 1, 10, custom_value ['note'], style11)

			sheet.write_merge(n+8, n+8, 11, 16, 'Checked By', style10)
			sheet.write_merge(n+9, n+11, 11, 16, '', style10)
			sheet.write_merge(n+12, n+12, 11, 16, 'Date Checked', style10)

			sheet.write_merge(n+8, n+8, 17, 22, 'Approved By', style10)
			sheet.write_merge(n+9, n+11, 17, 22, '', style10)
			sheet.write_merge(n+12, n+12, 17, 22, 'Date Approve', style10)

			col_width = 256 * 25
			try:
				for i in itertools.count():
					sheet.col(i).width = col_width
					sheet.col(0).width = 256 * 3
					sheet.col(1).width = 256 * 15
					sheet.col(2).width = 256 * 15
					sheet.col(3).width = 256 * 20
					sheet.col(4).width = 256 * 15
					sheet.col(5).width = 256 * 50
					sheet.col(6).width = 256 * 20
					sheet.col(7).width = 256 * 30
					sheet.col(8).width = 256 * 17
					sheet.col(9).width = 256 * 13
					sheet.col(10).width = 256 * 10
					sheet.col(11).width = 256 * 15
					sheet.col(12).width = 256 * 15
					sheet.col(13).width = 256 * 9
					sheet.col(14).width = 256 * 9
					sheet.col(15).width = 256 * 9
					sheet.col(16).width = 256 * 9
					sheet.col(17).width = 256 * 9
					sheet.col(18).width = 256 * 9
					sheet.col(19).width = 256 * 9
					sheet.col(20).width = 256 * 10
					sheet.col(21).width = 256 * 15
			except ValueError:
				pass

		if platform.system() == 'Linux':
			filename = ('/tmp/Picking Report' + '.xls')
		else:
			filename = ('Picking Report' + '.xls')

		workbook.save(filename)
		fp = open(filename, "rb")
		file_data = fp.read()
		out = base64.encodestring(file_data)
					   
# Files actions         
		attach_vals = {
				'picking_data': 'Picking Report'+ '.xls',
				'file_name': out,
			} 
			
		act_id = self.env['internal.transfer.report'].create(attach_vals)
		fp.close()
		return {
		'type': 'ir.actions.act_window',
		'res_model': 'internal.transfer.report',
		'res_id': act_id.id,
		'view_type': 'form',
		'view_mode': 'form',
		'context': self.env.context,
		'target': 'new',
		}