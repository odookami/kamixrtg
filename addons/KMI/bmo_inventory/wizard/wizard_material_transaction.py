import io
import re
import json
import time
from numpy import product
import pytz
import base64
import itertools
# from operator import itemgetter
from xlwt import easyxf
from odoo.http import request
from odoo.tools.misc import xlwt
from odoo.tools import date_utils
from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class ReportMaterial_Transaction(models.TransientModel):
	_name = 'material.transaction.wizard'
	_description = 'Material Transction Report'

	product_id = fields.Many2one('product.product', string='Product')
	all_lot = fields.Boolean("All Lot", default=True)
	lot_ids = fields.Many2many('stock.production.lot', string='Lot')
	data_file = fields.Binary('File')
	name = fields.Char('File Name')

	@api.onchange('product_id')
	def _onchange_product_id(self):
		for rec in self:
			return {'domain':{'lot_ids':[('product_id','in',self.product_id.ids)]}}

	@api.onchange('all_lot')
	def _onchange_all_lot(self):
		for rec in self:
			if rec.all_lot:
				rec.lot_ids = self.env['stock.production.lot'].search([]).ids
			else:
				rec.lot_ids = False

	# @api.onchange('product_id')
	# def _onchange_product_id(self):
	# 	lot = self.env['stock.production.lot'].search([('product_id','=',self.product_id.id)])
	# 	list_data = [x.id for x in lot]
	# 	return {'domain':{'lot_ids':[('id','in',list_data)]}}

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
				worksheet.col(0).width = 256 * 75
				worksheet.col(1).width = 256 * 15
				worksheet.col(2).width = 256 * 20
				worksheet.col(3).width = 256 * 20
				worksheet.col(4).width = 256 * 15
				worksheet.col(5).width = 256 * 10
				worksheet.col(6).width = 256 * 30
				worksheet.col(7).width = 256 * 30
		except ValueError:
			pass
		
		# print(self.lot_ids.ids,'==============')
		product = "pp.id = '%s'" % (self.product_id.id)

		# if len(self.lot_ids) >1:
		# 	l = [i.name for i in self.lot_ids]
		# 	# print('lllllllllllllllll', l)
		# 	# lot = f'lot.id in {tuple(self.lot_ids.ids)}'
		# 	lot = f'lot.name in {tuple(i for i in l)}'
		# else:
		# 	# lot = "lot.id = %s" % (self.lot_ids.id)
		# 	lot = "lot.name = %s" % ("'" + self.lot_ids.name + "'")
		
		# lot
		src_lot = self.env['stock.production.lot']
		if self.all_lot:
			dom_lot = [('product_id','in',self.product_id.ids)]
			l_src = src_lot.search(dom_lot)
			l = [i.name for i in l_src]
			lot = f'lot.name in {tuple(i for i in l)}'
		else:
			if len(self.lot_ids) == 1 :
				lot = "lot.name = '%s'" % (self.lot_ids.name)
			else:
				l = [i.name for i in self.lot_ids.ids]
				lot = f'lot.name in {tuple(i for i in l)}'

		sql_data = """ 
			SELECT
				sml.id as sml,
				sml.date as date,
				sml.reference as ref,
				pt.name as prod_name,
				pp.default_code as code,
				lot.name as lot_name,
				sl.name as from,
				sl2.name as to,
				sl2.usage as loc_type,
				sml.qty_done as qty,
				uom.name as uom,
				pick.id as picking,
				spt.code as type,
				mrp.id as mrp,
				spt2.code as type2,
				case when sl2.usage = 'internal' then sml.qty_done else 0 end as initial_p,
				case when sl2.usage in ('inventory loss', 'production', 'inventory', 'customer') then sml.qty_done *-1 else 0 end as initial_m
			FROM stock_move_line AS sml
				LEFT JOIN product_product pp ON (pp.id=sml.product_id)
					LEFT JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
				LEFT JOIN stock_production_lot lot ON (lot.id=sml.lot_id)
				LEFT JOIN stock_location sl ON (sl.id = sml.location_id)
				LEFT JOIN stock_location sl2 ON (sl2.id = sml.location_dest_id)
				LEFT JOIN uom_uom uom ON (uom.id = sml.product_uom_id)
				LEFT JOIN stock_picking pick ON (pick.id = sml.picking_id)
				LEFT JOIN stock_picking_type spt ON (spt.id = pick.picking_type_id)
				LEFT JOIN mrp_production mrp ON (mrp.id = sml.production_id)
				LEFT JOIN stock_picking_type spt2 ON (spt2.id = mrp.picking_type_id)
			WHERE
				sml.state = 'done' and sl.usage != sl2.usage and %s and %s
			ORDER BY lot.name, sml.date
		""" % (product, lot)
		self.env.cr.execute(sql_data)
		results = self.env.cr.dictfetchall()
		# print('====results======',results)	
		data = []
		minus = {}
		for i in results:
			qty = i['qty']
			print(i['type'],'====results======',i['type2'])	
			if i['loc_type'] in ['customer', 'inventory', 'production']:
				qty = -i['qty']
			if i['lot_name'] not in minus:
				minus[i['lot_name']] = [qty]
			else:
				minus[i['lot_name']]+=[qty]

			data.append({
				'Item Name': i['prod_name'],
				'Item Code': i['code'],
				'Date'     : i['date'].strftime("%d-%b-%Y"),
				'Lot'      : i['lot_name'],
				'Qty'      : i['qty'],
				'uom'      : i['uom'],
				'type'     : i['type'] or i['type2'],
				'Ref'      : i['ref'],
				'loc_type' : i['loc_type'],
			})

		header = ['Item Name' ,'Item Code','Date', 'Lot', 'Qty', 'uom', 'type', 'Ref']
		colh = -1
		for x in header:
			colh += 1
			style_table.alignment.wrap = 1
			worksheet.write(0, colh, x, style_table)
		
		no = 1
		for i in data:
			# if i['type'] == 'internal':
			# 	tipe = 'Internal Transfer'
			if i['type'] == 'incoming':
				tipe = 'Receipt'
			elif i['type'] == 'outgoing':
				tipe = 'Delivey'
			elif i['type'] == 'mrp_operation':
				tipe = 'Manufacturing'
			else:
				tipe = 'Inventory Adjustments'
			worksheet.write(no, 0, i['Item Name'], style_table) 
			worksheet.write(no, 1, i['Item Code'], style_table) 
			worksheet.write(no, 2, i['Date'], style_table) 
			worksheet.write(no, 3, i['Lot'], style_table)
			worksheet.write(no, 4, i['Qty'] * -1 if i['loc_type'] in ['customer', 'inventory', 'production'] else i['Qty'], style_table)            
			worksheet.write(no, 5, i['uom'], style_table)
			worksheet.write(no, 6, tipe, style_table) 
			worksheet.write(no, 7, i['Ref'], style_table)
			no+=1

		# no = 0
		# for line in data:
		# 	no += 1
		# 	col = -1
		# 	for i in header:
		# 		col += 1
		# 		worksheet.write(no, col, line[i], style_table)
		
		if data:
			n = no+1; ke= 3
			worksheet.write_merge(n, n+len(minus)-1, 0, 2, 'Jumlah', style_table)
			k = [k for k,v in minus.items()] 
			for i in k:
				worksheet.write(n, ke, i, style_table)
				n+=1

			ni = no+1; r=4
			for k, v in minus.items():
				a= sum(v)
				worksheet.write(ni, r, a, style_table)
				ni+=1

		file_data = io.BytesIO()
		book.save(file_data)
		filename = 'Report Material Transaction %s .xls'  % (self.product_id.code)
		out = base64.encodestring(file_data.getvalue())
		self.write({'data_file': out, 'name': filename})

		view = self.env.ref('bmo_inventory.material_transaction_wizard_form')
		return {
			'view_type': 'form',
			'views': [(view.id, 'form')],
			'view_mode': 'form',
			'res_id': self.id,
			'res_model': 'material.transaction.wizard',
			'type': 'ir.actions.act_window',
			'target': 'new',
		}