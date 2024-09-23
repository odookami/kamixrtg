# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from os import stat
import re, io
import xlwt
import base64
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
	
	date_start = fields.Date('Date Start')
	# @api.multi
	def action_picking_report(self):          
		
		judul = "Report QC"
		header = ['NO', 'Kedatangan', 'Pengecekan', 'DO Number', 'Item Code', 'Product', 'LOT Number',\
					'Manufacture Plant', 'Country of Origin', 'Quantity', 'UOM', 'Date', 'Production',\
					'Expiry','CoA/RoA', 'ASL', 'Bocor', 'Rusak', 'Kotor', 'Basah', 'Pest', 'Status', 'Note']

		workbook = xlwt.Workbook()                  
		picking = self.env['stock.picking'].browse(self._context.get('active_ids', list()))    

		if self.date_start:
			date_start = (datetime.strptime(str(self.date_start), \
					'%Y-%m-%d') + timedelta(hours=7)).strftime("%Y-%m-%d")
			where_period = "pick.scheduled_date >= '%s'" % (date_start)

		# for pick in picking: 
			# print(pick.name,'====================')

		sql_qc = """
			SELECT
				pick.id AS id,
				pick.scheduled_date AS kedatangan,
				pick.date_done AS pengecekan,
				pick.origin AS do_number,
				pt.default_code AS item_code,
				pt.name AS product,
				sml.lot_name AS lot,
				rp.name AS vendor,
				sml.qty_done AS quantity,
				u.name AS uom,
				sml.expiration_date AS expiry,

				sml.status_qc AS status,
				irs.name AS note,
				
				pick.name AS pick_name
			FROM inventory_quality_check AS iqc
				LEFT JOIN stock_move_line sml ON (sml.id=iqc.move_line_id)
				LEFT JOIN inventory_reject_reason irs ON (irs.id=sml.reason_id)
				LEFT JOIN product_product p ON (sml.product_id=p.id)
				LEFT JOIN product_template pt ON (p.product_tmpl_id=pt.id)
				LEFT JOIN uom_uom u ON (u.id=pt.uom_id)
				LEFT JOIN stock_move sm ON (sm.id=sml.move_id)
				LEFT JOIN res_partner rp ON (rp.id=sm.vendor_id)
				LEFT JOIN stock_picking pick ON (pick.id=sm.picking_id)
			WHERE 
				%s
			Group By
				pick.id,
				pick.scheduled_date,
				pick.date_done,
				pick.origin,
				pt.default_code,
				pt.name,
				sml.lot_name,
				rp.name,
				sml.qty_done,
				u.name,
				sml.expiration_date,

				sml.status_qc,
				irs.name,
				pick.name
			Order By
				sml.lot_name ASC

		""" % (where_period)
	
		self.env.cr.execute(sql_qc)
		results = self.env.cr.dictfetchall()
		# print('result==============',results)

		custom_value = {}
		sml = []        
		for rec in results:
			product = {}

			product ['date_done'] = rec['pengecekan'].strftime("%Y-%m-%d") if rec['pengecekan'] else ''
			product ['product_id_code'] = rec['item_code'] or ''
			product ['product_id_name'] = rec['product'] or ''
			product ['lot_number'] = rec['lot'] or ''
			product ['qty_done'] = rec['quantity'] or ''
			product ['product_uom'] = rec['uom'] or ''
			product ['date_prod'] = ''
			product ['date_expry'] = rec['expiry'].strftime("%Y-%m-%d") if rec['expiry'] else ''
			product ['status'] = rec['note'] or ''
			product ['status_qc'] = rec['note'] or ''
			product ['note_qc'] = rec['note'] or ''

			sml.append(product)
			
			custom_value ['reference'] = rec['pick_name']   
			custom_value ['scheduled_date'] = rec['kedatangan'].strftime("%Y-%m-%d") or ''
			custom_value ['source_document'] = rec['do_number'] or ''
			custom_value ['vendor_id'] = rec['vendor']
		custom_value['products_sml'] = sml
		custom_value ['country'] = 'Indonesia'
												
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
		style8_1 = xlwt.easyxf('borders:right thin;', num_format_str='#,##0.00')
		sheet = workbook.add_sheet('pick.name')

		sheet.write(5, 1, 'No Receipt :', style1)
		# sheet.write(5, 2, custom_value['reference'], style1)     
		# sheet.write(5, 1, 'Scheduled Date :', style1)
		# sheet.write(5, 2, custom_value['reference'], style1)  
		#    
		sheet.write_merge(9, 10, 1, 1, 'NO', style1)        
		sheet.write_merge(9, 10, 2, 2, 'Kedatangan', style1)
		sheet.write_merge(9, 10, 3, 3, 'Pengecekan', style1)
		sheet.write_merge(9, 10, 4, 4, 'DO Number', style1)
		sheet.write_merge(9, 10, 5, 5, 'Item Code', style1)
		sheet.write_merge(9, 10, 6, 6, 'PRODUCT', style1)
		sheet.write_merge(9, 10, 7, 7, 'LOT NUMBER', style1)
		sheet.write_merge(9, 10, 8, 8, 'Manufacturer Plant', style1)  
		sheet.write_merge(9, 10, 9, 9, 'Counry Of Origin', style1)      
		sheet.write_merge(9, 10, 10, 10, 'Quantity', style1)
		sheet.write_merge(9, 10, 11, 11, 'UOM', style1)
		sheet.write_merge(9, 9, 12, 13, 'Date', style1)
		sheet.write(10, 12, 'Production', style1)
		sheet.write(10, 13, 'Expired', style1)
		sheet.write_merge(9, 9, 14, 15, 'Document', style1)
		sheet.write(10, 14, 'CoA/RoA', style1)
		sheet.write(10, 15, 'ASL', style1)
		sheet.write_merge(9, 9, 16, 20, 'Kondisi', style1)
		sheet.write(10, 16, 'Bocor', style1)
		sheet.write(10, 17, 'Rusak', style1)
		sheet.write(10, 18, 'Kotor', style1)
		sheet.write(10, 19, 'Basah', style1)
		sheet.write(10, 20, 'Pest', style1)
		sheet.write_merge(9, 10, 21, 21, 'Status', style1)
		sheet.write_merge(9, 10, 22, 22, 'Note', style1)

		n = 11; m=10; i = 1
		
		for product in custom_value['products_sml']:
			# print('==================================',product)
			
			sheet.write(n, 1, i, style5)  
			sheet.write(n, 2, custom_value['scheduled_date'], style6) 
			sheet.write(n, 3, product['date_done'], style6) 
			sheet.write(n, 4, custom_value['source_document'], style6) 
			sheet.write(n, 5, product['product_id_code'], style6)
			sheet.write(n, 6, product['product_id_name'], style6)            
			sheet.write(n, 7, product['lot_number'], style0)
			sheet.write(n, 8, custom_value['vendor_id'], style0)
			sheet.write(n, 9, custom_value['country'], style0)
			sheet.write(n, 10, product['qty_done'], style0)
			sheet.write(n, 11, product['product_uom'], style0)
			sheet.write(n, 12, product['date_prod'], style0)
			sheet.write(n, 13, product['date_expry'], style0)
			# sheet.write(n, 15, product['status'][0], style0)
			# sheet.write(n, 16, product['status'][1], style0)
			# sheet.write(n, 17, product['status'][2], style0)
			# sheet.write(n, 18, product['status'][3], style0)
			# sheet.write(n, 19, product['status'][4], style0)
			# sheet.write(n, 20, product['status'][5], style0)
			# sheet.write(n, 21, product['status'][6], style0)
			sheet.write(n, 21, product['status_qc'], style0)
			sheet.write(n, 22, product['note_qc'], style0)

			n += 1; m +=1; i += 1

		col_width = 256 * 25
		try:
			for i in itertools.count():
				sheet.col(i).width = col_width
				sheet.col(0).width = 256 * 15
				sheet.col(1).width = 256 * 10
				sheet.col(2).width = 256 * 15
				sheet.col(3).width = 256 * 15
				sheet.col(4).width = 256 * 15
				sheet.col(5).width = 256 * 15
				sheet.col(6).width = 256 * 50
				sheet.col(7).width = 256 * 20
				sheet.col(8).width = 256 * 20
				sheet.col(9).width = 256 * 17
				sheet.col(10).width = 256 * 13
				sheet.col(11).width = 256 * 10
				sheet.col(12).width = 256 * 15
				sheet.col(13).width = 256 * 15
				sheet.col(14).width = 256 * 9
				sheet.col(15).width = 256 * 7
				sheet.col(16).width = 256 * 7
				sheet.col(17).width = 256 * 7
				sheet.col(18).width = 256 * 7
				sheet.col(19).width = 256 * 7
				sheet.col(20).width = 256 * 7
				sheet.col(21).width = 256 * 13
				sheet.col(22).width = 256 * 13
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



		# file_data = io.BytesIO()
		# book.save(file_data)

		# if self.tipe_data in ('so'):
		# 	filename = 'report_invoice_customer_%s_to_%s_on_%s.xls' % \
		# 		(self.date_start, self.date_end, now.strftime("%Y-%m-%d"))
		# elif self.tipe_data in ('pos'):
		# 	filename = 'report_pos_%s_to_%s_on_%s.xls' % \
		# 		(self.date_start, self.date_end, now.strftime("%Y-%m-%d"))
		# else:
		# 	filename = 'report_so_&_pos_%s_to_%s_on_%s.xls' % \
		# 		(self.date_start, self.date_end, now.strftime("%Y-%m-%d"))

		# out = base64.encodestring(file_data.getvalue())
		# self.write({'data_file': out, 'name': filename})

		# view = self.env.ref('sbp_sale.form_wizard_report_sales')
		# return {
		# 	'view_type': 'form',
		# 	'views': [(view.id, 'form')],
		# 	'view_mode': 'form',
		# 	'res_id': self.id,
		# 	'res_model': 'wizard.report.sales',
		# 	'type': 'ir.actions.act_window',
		# 	'target': 'new',
		# }