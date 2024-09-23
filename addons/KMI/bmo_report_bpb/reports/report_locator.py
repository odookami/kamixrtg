import io
import re
import json
import time
from numpy import product
import pytz
import base64
import itertools
from xlwt import easyxf
from odoo.http import request
from odoo.tools.misc import xlwt
from odoo.tools import date_utils
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, Warning as UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class StockCardLocator(models.TransientModel):
	_name = 'stock.card.locator'
	_description = 'Material Transction Report'

	all_product = fields.Boolean("All Product")
	product_ids = fields.Many2many(comodel_name="product.product", string="Products")
	
	all_lot = fields.Boolean("All Lot", default=True)
	lot_ids = fields.Many2many("stock.production.lot", string="Lot")

	all_loc = fields.Boolean("All Location", default=True)
	location_ids = fields.Many2many('stock.location', string='Location')
	
	data_file = fields.Binary('File')
	name = fields.Char('File Name')

	@api.onchange('product_ids')
	def _onchange_product_ids(self):
		for rec in self:
			return {'domain':{'lot_ids':[('product_id','in',self.product_ids.ids)]}}
	
	@api.onchange('all_lot')
	def _onchange_all_lot(self):
		for rec in self:
			if rec.all_lot:
				rec.lot_ids = self.env['stock.production.lot'].search([]).ids
			else:
				rec.lot_ids = False
	
	@api.onchange('all_loc')
	def _onchange_all_loc(self):
		for rec in self:
			if rec.all_loc:
				rec.location_ids = self.env['stock.location'].search([]).ids
			else:
				rec.location_ids = False
	
	@api.onchange('all_product')
	def _onchange_all_product(self):
		for rec in self:
			if rec.all_product:
				rec.product_ids = self.env['product.product'].search([]).ids
				rec.lot_ids = self.env['stock.production.lot'].search([]).ids
			if rec.all_product == False:
				rec.product_ids = False
	
	def eksport_excel(self):
		book = xlwt.Workbook()
		worksheet = book.add_sheet("sheet 1", cell_overwrite_ok=True)
		style_no_bold = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin;'
			'align: vert centre, horz left; font: name Helvetica Neue;')
		style_no_bold.num_format_str = '#,##0.00'

		style_header = xlwt.easyxf('font: colour black, bold 1, name Helvetica Neue; borders: left thin, right thin, top thin,'
			'bottom thin; align: vert centre, horz center; ')

		style_table = xlwt.easyxf('font: colour black, bold 1, name Helvetica Neue; align: vert centre, horz center, wrap true;'
									"borders: top thin,left thin,right thin,bottom thin")
		style_table.num_format_str = '#,##0.0000'
		style_template = xlwt.easyxf('font: colour black, bold 1, name Helvetica Neue;')

		col_width = 256 * 25
		try:
			for i in itertools.count():
				worksheet.col(i).width = col_width
				worksheet.col(0).width = 256 * 20
				worksheet.col(1).width = 256 * 75
				worksheet.col(2).width = 256 * 35
				worksheet.col(3).width = 256 * 15
				worksheet.col(4).width = 256 * 25
				worksheet.col(5).width = 256 * 20
				worksheet.col(6).width = 256 * 15
				worksheet.col(7).width = 256 * 15
				worksheet.col(8).width = 256 * 15
				worksheet.col(9).width = 256 * 8
		except ValueError:
			pass
		
		src_loc = self.env['stock.location']
		src_lot = self.env['stock.production.lot']

		# product
		if len(self.product_ids) >1:
			p = [i.id for i in self.product_ids]
			product = f'pp.id in {tuple(i for i in p)}'
		else:
			product = "pp.id = %s" % (self.product_ids.id)

		# lot
		if self.all_lot:
			dom_lot = [('product_id','in',self.product_ids.ids)]
			l_src = src_lot.search(dom_lot)
			l = [i.name for i in l_src]
			lot = f'lot.name in {tuple(i for i in l)}'
		else:
			if len(self.lot_ids) == 1 :
				lot = "lot.name = '%s'" % (self.lot_ids.name)
			else:
				l = [i.name for i in self.lot_ids.ids]
				lot = f'lot.name in {tuple(i for i in l)}'
				
		# location
		loc = [i.id for i in self.location_ids]
		if self.all_loc:
			location = f'sl.id in {tuple(i for i in loc)}'
		else:
			loc_src = src_loc.search(
				[("id", "child_of", [i for i in loc])])

			if len(loc_src) == 1:
				raise ValidationError(_('Lokasi ini bukan Lokasi Parent'))
			else:
				location = f'sl.id in {tuple(loc_src.ids)}'

		sql_data = """ 
			SELECT
				pt.name as prod_name,
				pt.default_code as prod_code,
				sl.complete_name as loc_name,
				sl.usage as loc_type,
				lot.name as lot,
				sq.expiration_date as exp_date,
				pack.name as pack,
				sq.quantity as qty,
				sq.reserved_quantity as reserved_qty,
				uom.name as uom,
				sum(sq.quantity - sq.reserved_quantity) as avail_qty
			FROM stock_quant AS sq
				LEFT JOIN product_product pp ON (pp.id=sq.product_id)
					LEFT JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
					LEFT JOIN uom_uom uom ON (uom.id = pt.uom_id)
				LEFT JOIN stock_location sl ON (sl.id = sq.location_id)
				LEFT JOIN stock_production_lot lot ON (lot.id=sq.lot_id)
				LEFT JOIN stock_quant_package pack ON (pack.id = sq.package_id)
			WHERE
				%s and %s and %s
			GROUP BY
				pt.name,
				pt.default_code,
				sl.complete_name,
				sl.usage,
				lot.name,
				sq.expiration_date,
				pack.name,
				sq.quantity,
				sq.reserved_quantity,
				uom.name
			ORDER BY prod_name
		""" % (product, lot, location)
		self.env.cr.execute(sql_data)
		results = self.env.cr.dictfetchall()
		# print('====results======',results)	
		data = []
		for i in results:
			if i['loc_type'] == 'internal' and i['qty'] > 0:
				data.append({
					'Item Code'	   : i['prod_code'],
					'Item Name'	   : i['prod_name'],
					'Locator'      : i['loc_name'],
					'No Pallet'    : i['pack'],
					'Lot'		   : i['lot'],
					'Exp Date'     : i['exp_date'].strftime("%d-%b-%Y") if i['exp_date'] else '',
					'Reserved Qty' : i['reserved_qty'],
					'Available Qty': i['avail_qty'],
					'On Hand Qty'  : i['qty'],
					'UOM'      	   : i['uom'],
				})

		header = ['Item Code', 'Item Name', 'Locator', 'No Pallet', 'Lot', 'Exp Date', 'On Hand Qty', 'Reserved Qty', 'Available Qty', 'UOM']
		colh = -1
		for x in header:
			colh += 1
			style_table.alignment.wrap = 1
			worksheet.write(0, colh, x, style_table)
		
		# no = 1
		# for i in data:
		# 	worksheet.write(no, 0, i['Item Code'], style_table) 
		# 	worksheet.write(no, 1, i['Item Name'], style_table) 
		# 	worksheet.write(no, 2, i['Locator'], style_table)
		# 	worksheet.write(no, 3, i['No Pallet'], style_table)
		# 	worksheet.write(no, 4, i['Lot'], style_table)
		# 	worksheet.write(no, 5, i['Exp Date'], style_table) 
		# 	worksheet.write(no, 6, i['Reserved Qty'], style_table)            
		# 	worksheet.write(no, 7, i['Available Qty'], style_table)            
		# 	worksheet.write(no, 8, i['On Hand Qty'], style_table)            
		# 	worksheet.write(no, 9, i['UOM'], style_table)
		# 	no+=1

		no = 0
		for line in data:
			no += 1
			col = -1
			for i in header:
				col += 1
				worksheet.write(no, col, line[i], style_table)
		
		file_data = io.BytesIO()
		book.save(file_data)
		filename = 'Stock Card Locator.xls'
		out = base64.encodestring(file_data.getvalue())
		self.write({'data_file': out, 'name': filename})

		view = self.env.ref('bmo_report_bpb.stock_card_locator_form')
		return {
			'view_type': 'form',
			'views': [(view.id, 'form')],
			'view_mode': 'form',
			'res_id': self.id,
			'res_model': 'stock.card.locator',
			'type': 'ir.actions.act_window',
			'target': 'new',
		}