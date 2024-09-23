import io
import time
import base64
import itertools
from io import StringIO

from odoo.tools.misc import xlwt
from dateutil import relativedelta
from collections import defaultdict
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class StockValuationWizard(models.TransientModel):
    _name = "report.stock.valuation.wizard"
    _description = "Stock Valuation"

    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product", required=True)
    location_id = fields.Many2one(comodel_name="stock.location", required=False)
    categ_ids = fields.Many2many(comodel_name="product.category")
    all_product = fields.Boolean("All Product")
    data_file       = fields.Binary('File')
    name            = fields.Char('File Name')
    
    @api.onchange('all_product')
    def _onchange_all_product(self):
        for rec in self:
            if rec.all_product:
                rec.product_ids = self.env['product.product'].search([]).ids
            if rec.all_product == False:
                rec.product_ids = False
    
    @api.onchange('categ_ids')
    def _onchange_categ_id(self):
        for rec in self:
            rec.product_ids = self.env['product.product'].search([('categ_id','=',rec.categ_ids.ids)]).ids
    
    @api.onchange('date_from')
    def _onchange_date_start(self):
        if self.date_from:
            self.date_to = self.date_from + relativedelta(months=1) - relativedelta(days=1)

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        date_to = self.date_to or fields.Date.context_today(self)
        where_date_from = "move_line.date < '%s 00:00:00'" % (date_from)
        where_date_to = "move_line.date <= '%s 17:00:00'" % (date_to)
        if len(self.product_ids.ids) == 1:
            where_product = "move_line.product_id = %s" % (self.product_ids.id)
        else:
            where_product = f'move_line.product_id in {tuple(self.product_ids.ids)}'
        where_location = "sl_from.name NOT LIKE 'External%' and sl_from.name NOT LIKE 'Internal%'"
        sql = """ 
            SELECT
                move_line.id,
                move_line.date,
                move_line.move_id,
                move_line.product_id,
                move_line.product_uom_id,
                move_line.location_id, 
                move_line.location_dest_id, 
                move_line.qty_done,
                case when %s then True else False end as is_initial
            FROM stock_move_line move_line
                join stock_location sl_from on move_line.location_id=sl_from.id 
                join stock_location sl_to on move_line.location_dest_id=sl_to.id 
            WHERE(sl_from.usage in ('production','inventory','customer') or sl_to.usage in ('production','inventory','customer')) and 
                move_line.location_id != move_line.location_dest_id and move_line.state = 'done' and %s and %s and %s and (move_line.not_adjust isnull or move_line.not_adjust=false)
        """ % (where_date_from, where_product, where_date_to,where_location)
        self._cr.execute(sql)
        stock_card_results = self._cr.dictfetchall()
        return stock_card_results
    
    def _compute_dict(self, data):
        if self.date_from.strftime("%m-%Y") != self.date_to.strftime("%m-%Y"):
            raise UserError(_("Mohon Pilih bulan yang sama"))
        dict_data = {}
        data_revisi_qty = []
        for x in data:
            product = self.env['product.product'].browse(x['product_id'])
            prod_rev = self.env['revisi.onhand'].sudo().search([('product_id','=',product.id)], limit=1)
            move = self.env['stock.move'].browse(x['move_id'])
            product_uom = self.env['uom.uom'].browse(x['product_uom_id'])
            location = self.env['stock.location'].browse(x['location_id'])
            location_dest = self.env['stock.location'].browse(x['location_dest_id'])
            qty = x['qty_done']
            if product_uom.id != product.uom_id.id:
                qty = product_uom._compute_quantity(qty, product.uom_id)
            if location_dest.usage in ('supplier','production','inventory','customer'):
                qty = -qty
                    
            if x['is_initial'] == True:
                if x['date'] <= datetime.strptime('2022-05-01 17:00:00', '%Y-%m-%d %H:%M:%S'):
                    if  prod_rev and prod_rev.id not in data_revisi_qty:
                        data_revisi_qty.append(prod_rev.id)
                        if prod_rev.product_id.id not in dict_data:
                            dict_data[prod_rev.product_id.id] = {'Awal' : [prod_rev.qty]}
                        else:
                            if 'Awal' not in dict_data[prod_rev.product_id.id]:
                                dict_data[prod_rev.product_id.id]['Awal'] = [prod_rev.qty]
                            else:
                                dict_data[prod_rev.product_id.id]['Awal'].append(prod_rev.qty)
                    else:
                        if product.id not in dict_data:
                            dict_data[product.id] = {'Awal' : [0]}
                        else:
                            if 'Awal' not in dict_data[product.id]:
                                dict_data[product.id]['Awal'] = [0]
                            else:
                                dict_data[product.id]['Awal'].append(0)
                else:
                    if product.id not in dict_data:
                        dict_data[product.id] = {'Awal' : [qty]}
                    else:
                        if 'Awal' not in dict_data[product.id]:
                            dict_data[product.id]['Awal'] = [qty]
                        else:
                            dict_data[product.id]['Awal'].append(qty)
            else:
                if location.usage == 'production':
                    # qty = move.production_id.goods_qty
                    if product.id not in dict_data:
                        dict_data[product.id] = {'Produksi' : [qty]}
                    else:
                        if 'Produksi' not in dict_data[product.id]:
                            dict_data[product.id]['Produksi'] = [qty]
                        else:
                            dict_data[product.id]['Produksi'].append(qty)
                elif location_dest.usage == 'production':
                    if product.id not in dict_data:
                        dict_data[product.id] = {'Produksi_Out' : [qty]}
                    else:
                        if 'Produksi_Out' not in dict_data[product.id]:
                            dict_data[product.id]['Produksi_Out'] = [qty]
                        else:
                            dict_data[product.id]['Produksi_Out'].append(qty)
                elif (location_dest.usage == 'inventory' and location_dest.scrap_location == False) or location.usage == 'inventory':
                    if product.id not in dict_data:
                        dict_data[product.id] = {'ADJ' : [qty]}
                    else:
                        if 'ADJ' not in dict_data[product.id]:
                            dict_data[product.id]['ADJ'] = [qty]
                        else:
                            dict_data[product.id]['ADJ'].append(qty)
                elif (location_dest.usage == 'inventory' and location_dest.scrap_location == True) or location.usage == 'inventory':
                    if product.id not in dict_data:
                        dict_data[product.id] = {'Reject' : [qty]}
                    else:
                        if 'Reject' not in dict_data[product.id]:
                            dict_data[product.id]['Reject'] = [qty]
                        else:
                            dict_data[product.id]['Reject'].append(qty)
                else:
                    if move.picking_id and move.picking_id.sale_id:
                        if product.id not in dict_data:
                            dict_data[product.id] = {'DO' : [qty]}
                        else:
                            if 'DO' not in dict_data[product.id]:
                                dict_data[product.id]['DO'] = [qty]
                            else:
                                dict_data[product.id]['DO'].append(qty)
                    else:
                        if product.id not in dict_data:
                            dict_data[product.id] = {'DO NOT SO' : [qty]}
                        else:
                            if 'DO NOT SO' not in dict_data[product.id]:
                                dict_data[product.id]['DO NOT SO'] = [qty]
                            else:
                                dict_data[product.id]['DO NOT SO'].append(qty)
        return dict_data
            
    def eksport_excel(self):
        book = xlwt.Workbook()
        sheet = book.add_sheet("Sheet 1", cell_overwrite_ok=True)
        now = datetime.now()
        
        style_no_bottom_border = xlwt.easyxf('font: name Calibri, height 260, \
            bold 1;align: horz center')

        header_style = xlwt.easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz center;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")
        
        left_header_style = xlwt.easyxf('font:height 200;pattern: pattern solid, fore_color gray25;'
                              'align: horiz left;font: color black; font:bold True;'
                              "borders: top thin,left thin,right thin,bottom thin")
        text_left = xlwt.easyxf('font:height 200; align: horiz left;')
        text_center = xlwt.easyxf('font: name Calibri; align: vert centre, horz center')
        style_bold_left = xlwt.easyxf('font: name Calibri, height 240, bold 1; \
            align: horz left')
        style_header2 = xlwt.easyxf('font: name Calibri, height 210, bold 1; \
            pattern: pattern solid, fore_colour yellow;borders: left thin, \
            right thin, top thin, bottom thin;align: vert centre, horz center')
        style_no_bold = xlwt.easyxf('font: name Calibri; align: vert centre, horz center')
        style_no_bold.num_format_str = '#,##0.0000'

        header = [
            'Location','Item Code', 'Product','Qty Awal','Nilai Awal','Qty Produksi', 'Nilai Qty Produksi', 'Qty Produksi Out', 'Nilai Qty Produksi Out',
            'Qty ADJ', 'Nilai ADJ','Qty Reject', 'Nilai Reject', 'Qty DO', 'Nilai DO', 'Qty DO NOT SO', 'Nilai DO NOT SO', 'Qty Akhir', 'Nilai PMAC', 'Nilai Akhir']

        result = self._compute_results()
        data_dict = self._compute_dict(result)
        colh = -1
        for x in header:
            colh += 1
            style_header2.alignment.wrap = 1
            sheet.write(3, colh, x, style_header2)
        
        no = 3
        for k, v in data_dict.items():
            product = self.env['product.product'].browse(k)
            date_from_old = self.date_from - relativedelta(months=1)
            date_end_old = date_from_old + relativedelta(months=1) - relativedelta(days=1)
            svl_old_obj = sum(self.env['stock.valuation.layer'].search([('product_id','=',product.id),('create_date','>=',date_from_old),('create_date','<=',date_end_old)], limit=1).mapped('unit_cost_new'))
            if svl_old_obj <= 0:
                svl_old_obj = product.standard_price
            
            bulan_from_new = self.date_from.strftime("%m")
            tahun_from_new = self.date_from.strftime("%Y")
            bulan_to_new = self.date_to.strftime("%m")
            tahun_to_new = self.date_from.strftime("%Y")
            cost_mrp = self.env['mrp.cost'].search([('select_month','>=',bulan_from_new),('select_year','>=',tahun_from_new),('select_month','<=',bulan_to_new),('select_year','<=',tahun_to_new)])
            cost_mrp_line = self.env['mrp.valuation.adjustment.lines'].search([('cost_id','in',cost_mrp.ids),('product_id','=',product.id)])
            if cost_mrp_line:
                value_pmac = cost_mrp_line.pmac
            else:
                value_pmac = product.standard_price
            no += 1
            Awal = Produksi = Produksi_out = ADJ = Reject = DO = DOS = 0
            if 'Awal' in v:
                Awal = sum(v['Awal'])
            if 'Produksi' in v:
                Produksi = sum(v['Produksi'])
            if 'Produksi_Out' in v:
                Produksi_out = sum(v['Produksi_Out'])
            if 'ADJ' in v:
                ADJ = sum(v['ADJ'])
            if 'Reject' in v:
                Reject = sum(v['Reject'])
            if 'DO' in v:
                DO = sum(v['DO'])
            if 'DO NOT SO' in v:
                DOS = sum(v['DO NOT SO'])
            akhir = Awal + Produksi + Produksi_out + ADJ + Reject + DO + DOS
            sheet.write(no, 0, "ALL", text_center)
            sheet.write(no, 1, str(product.default_code), text_center)
            sheet.write(no, 2, str(product.name), text_left)
            sheet.write(no, 3, Awal, style_no_bold)
            sheet.write(no, 4, svl_old_obj * Awal, style_no_bold)
            sheet.write(no, 5, Produksi, style_no_bold)
            sheet.write(no, 6, value_pmac * Produksi, style_no_bold)
            sheet.write(no, 7, Produksi_out, style_no_bold)
            sheet.write(no, 8, value_pmac * Produksi_out, style_no_bold)
            sheet.write(no, 9, ADJ, style_no_bold)
            sheet.write(no, 10, value_pmac * ADJ, style_no_bold)
            sheet.write(no, 11, Reject, style_no_bold)
            sheet.write(no, 12, value_pmac * Reject, style_no_bold)
            sheet.write(no, 13, DO, style_no_bold)
            sheet.write(no, 14, value_pmac * DO, style_no_bold)
            sheet.write(no, 15, DOS, style_no_bold)
            sheet.write(no, 16, value_pmac * DOS, style_no_bold)
            sheet.write(no, 17, akhir, style_no_bold)
            sheet.write(no, 18, value_pmac, style_no_bold)
            # sheet.write(no, 19, value_pmac * akhir, style_no_bold)
            sheet.write(no, 19, xlwt.Formula(f'R{no+1}*S{no+1})'), style=style_no_bold)
        
        col_width = 256 * 25
        try:
            for i in itertools.count():
                sheet.col(i).width = col_width
                sheet.col(2).width = 256 * 70
        except ValueError:
            pass

        file_data = io.BytesIO()
        book.save(file_data)
        filename= '%s %s.xls' % ('Stock Valuation', now)
        out = base64.encodestring(file_data.getvalue())
        self.write({'data_file': out, 'name': filename})

        view = self.env.ref('bmo_inventory.report_stock_valuation_wizard_form')
        return {
            'view_type': 'form',
            'views': [(view.id, 'form')],
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'report.stock.valuation.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }