import io
from numpy import product
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

class StockCardSummary(models.TransientModel):
	_name = 'stock.card.summary'
	_description = 'Stock Card Summary'

	date_from = fields.Date()
	date_to = fields.Date()
	all_product = fields.Boolean("All Product")
	product_ids = fields.Many2many(comodel_name="product.product", required=True)

	all_lot = fields.Boolean("All Lot", default=True)
	lot_ids = fields.Many2many("stock.production.lot", string="Lot")

	# all_loc = fields.Boolean("All Location", default=True)
	# location_ids = fields.Many2many('stock.location', string='Location')
	data_file = fields.Binary('File')
	name = fields.Char('File Name')

	@api.onchange('product_ids')
	def _onchange_product_ids(self):
		for rec in self:
			return {'domain':{'lot_ids':[('product_id','in',self.product_ids.ids)]}}

	@api.onchange('date_from')
	def _onchange_date_from(self):
		if self.date_from:
			self.date_to = self.date_from + relativedelta(months=1) - relativedelta(days=1)
	
	@api.onchange('all_lot')
	def _onchange_all_lot(self):
		for rec in self:
			if rec.all_lot:
				rec.lot_ids = self.env['stock.production.lot'].search([]).ids
			else:
				rec.lot_ids = False
	
	# @api.onchange('all_loc')
	# def _onchange_all_loc(self):
	# 	for rec in self:
	# 		if rec.all_loc:
	# 			rec.location_ids = self.env['stock.location'].search([]).ids
	# 		else:
	# 			rec.location_ids = False
	
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
				worksheet.col(1).width = 256 * 50
				worksheet.col(2).width = 256 * 25
				worksheet.col(3).width = 256 * 25
				worksheet.col(4).width = 256 * 20
				worksheet.col(5).width = 256 * 25
				worksheet.col(6).width = 256 * 25
				worksheet.col(7).width = 256 * 25
		except ValueError:
			pass

		worksheet.write(0, 0, 'Date From', style_table) 
		worksheet.write(0, 1, self.date_from.strftime("%d-%b-%Y"), style_table) 
		worksheet.write(1, 0, 'Date To', style_table)
		worksheet.write(1, 1, self.date_to.strftime("%d-%b-%Y"), style_table)
	
		# date_search
		date_from = self.date_from or "0001-01-01"
		date_to = self.date_to or fields.Date.context_today(self)
		where_date_from = "sml.date >= '%s 00:00:00'" % (date_from)
		where_date_to = "sml.date <= '%s 23:59:59'" % (date_to)
		# searce tgl dari date_from_to
		data_date_src = "sml.date between '%s 00:00:00' and '%s 00:00:00'" % (date_from, date_to)
		# print(where_date_from, '=====', where_date_to)

		# date M-1
		src_date_from = date_from - relativedelta(months=1)
		src_date_to = date_to - relativedelta(months=1)
		date_src = "sml.date between '%s 00:00:00' and '%s 00:00:00'" % (src_date_from, src_date_to)

		where_date_src = "sml.date between '%s 00:00:00' and '%s 00:00:00'" % (src_date_from, date_to)
		# print(date_src, '=====')

		# product
		if len(self.product_ids) >1:
			p = [i.id for i in self.product_ids]
			product = f'pp.id in {tuple(i for i in p)}'
		else:
			product = "pp.id = %s" % (self.product_ids.id)

		# lot
		src_lot = self.env['stock.production.lot']
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
		# src_loc = self.env['stock.location']
		# loc = [i.id for i in self.location_ids]
		# if self.all_loc:
		# 	location = f'sld.id in {tuple(i for i in loc)}'
		# else:
		# 	loc_src = src_loc.search(
		# 		[("id", "child_of", [i for i in loc])])

		# 	if len(loc_src) == 1:
		# 		raise ValidationError(_('Lokasi ini bukan Lokasi Parent'))
		# 	else:
		# 		location = f'sld.id in {tuple(loc_src.ids)}'
		
		sql_data = """ 
			SELECT
				pp.id as prod_id,
				pp.default_code as code,
				pt.name as prod_name,
				lot.name as lot_name,
				lot.expiration_date as exp_date,
				sml.qty_done as qty,
				sld.complete_name as loc_name,
				sld.usage as loc_type,
				case when %s and sld.usage = 'internal' then SUM(sml.qty_done) else 0 end as initial_p,
				case when %s and sld.usage in ('inventory loss', 'production', 'inventory', 'customer') then SUM(sml.qty_done)*-1 else 0 end as initial_m,
				case when %s and sld.usage = 'internal' then SUM(sml.qty_done) else 0 end as in_qty,
				case when %s and sld.usage in ('inventory loss', 'production', 'inventory', 'customer') then SUM(sml.qty_done) else 0 end as out_qty
			FROM stock_move_line AS sml
				LEFT JOIN product_product pp ON (pp.id=sml.product_id)
					LEFT JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
				LEFT JOIN stock_production_lot lot ON (lot.id=sml.lot_id)
				LEFT JOIN stock_location sl ON (sl.id = sml.location_id)
				LEFT JOIN stock_location sld ON (sld.id = sml.location_dest_id)
			WHERE
				sml.state = 'done' and %s and %s and %s and sl.usage != sld.usage
			GROUP BY
				pp.id,
				pp.default_code,
				pt.name,
				lot.name,
				lot.expiration_date,
				sml.qty_done,
				sml.date,
				sld.complete_name,
				sld.usage
			ORDER BY pt.name, lot.name
		""" % (date_src, date_src, data_date_src, data_date_src, product, lot, where_date_src)
		self.env.cr.execute(sql_data)
		results = self.env.cr.dictfetchall()
		# print('====results======',results)	
		data = []
		res = {}
		for i in results:
			date_exp = i['exp_date'].strftime("%d-%b-%Y") if i['exp_date'] else ''
			if i['prod_id'] not in res:
				res[i['prod_id']]={
					i['lot_name']:{ 
						date_exp:{
							'qty_awal_p': [i['initial_p']],
							'qty_awal_m': [i['initial_m']],
							'in': [i['in_qty']],
							'out': [i['out_qty']],
						}
					}
				}
			else:
				if i['lot_name'] not in res[i['prod_id']]:
					res[i['prod_id']][i['lot_name']]={
						date_exp:{
						  'qty_awal_p': [i['initial_p']],
						  'qty_awal_m': [i['initial_m']],
						  'in': [i['in_qty']],
						  'out': [i['out_qty']],
						}
					}
				else:
					# print(i['exp_date'],'===exps==',i['exp_date'])
					if date_exp not in res[i['prod_id']][ i['lot_name']]:
						res[i['prod_id']][i['lot_name']][date_exp]={ 
							'qty_awal_p': [i['initial_p']],
							'qty_awal_m': [i['initial_m']],
							'in': [i['in_qty']],
							'out': [i['out_qty']],
						}
					else:
						res[i['prod_id']][i['lot_name']][date_exp]['qty_awal_p'].append((i['initial_p']))
						res[i['prod_id']][i['lot_name']][date_exp]['qty_awal_m'].append((i['initial_m']))
						res[i['prod_id']][i['lot_name']][date_exp]['in'].append(i['in_qty'])
						res[i['prod_id']][i['lot_name']][date_exp]['out'].append(i['out_qty'])

			no = 5
			for k, v in res.items():
				prod = self.env['product.product'].browse(k)
				worksheet.write(no, 0, prod.default_code, style_table)
				worksheet.write(no, 1, prod.name, style_table)
				for u, i in v.items():
					worksheet.write(no, 3, u, style_table)
					for a, b in i.items():
						qty_awal_p = sum(b['qty_awal_p'])
						qty_awal_m = sum(b['qty_awal_m'])
						qty_awal = qty_awal_p + qty_awal_m
						qty_in = sum(b['in'])
						qty_out = sum(b['out']) * -1
						worksheet.write(no, 2, qty_awal, style_table)
						worksheet.write(no, 4, a, style_table)
						worksheet.write(no, 5, qty_in, style_table)
						worksheet.write(no, 6, qty_out, style_table)
						worksheet.write(no, 7, qty_awal+qty_in+qty_out, style_table)
						# print(qty_in,'====bbbbb', qty_out)
						no+=1

		# print('===',res)
		header = ['Item Code', 'Description', 'Qty Awal', 'Lot Number', 'Exp Date', 'In Qty', 'Out Qty', 'Balance']
		colh = -1
		for x in header:
			colh += 1
			style_table.alignment.wrap = 1
			worksheet.write(4, colh, x, style_table)
		
		file_data = io.BytesIO()
		book.save(file_data)
		filename = 'Stock Card Summary.xls'
		out = base64.encodestring(file_data.getvalue())
		self.write({'data_file': out, 'name': filename})

		view = self.env.ref('bmo_report_bpb.stock_card_summary_form')
		return {
			'view_type': 'form',
			'views': [(view.id, 'form')],
			'view_mode': 'form',
			'res_id': self.id,
			'res_model': 'stock.card.summary',
			'type': 'ir.actions.act_window',
			'target': 'new',
		}