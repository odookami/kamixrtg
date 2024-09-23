# -*- coding: utf-8 -*-
import io
import xlrd
import json
import pytz
import base64
import openpyxl 
import itertools
import calendar
from collections import OrderedDict
from xlwt import easyxf
from odoo.http import request
from odoo.tools.misc import xlwt
from odoo.tools import date_utils
from odoo import api, fields, models, _
from odoo.exceptions import Warning as UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class MrpMaterialUsage(models.TransientModel):
    _name = 'mrp.material.usage'
    _description = 'Material Usage'

    name = fields.Char(string='Name')
    data_file = fields.Binary('File')
    report_type = fields.Selection(string='Type', 
        selection=[('Mixing', 'Mixing'), ('Filling', 'Fill-Pack'), 
        ('Banded', 'Banded')], default='Mixing')
    batch_mrp_id = fields.Many2one('batch.mrp.production', string='Batch MRP')
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'), ('to_close', 'To Close'), ('done', 'Close'),
        ('cancel', 'Cancelled'), ('all', 'All Status')], default='all', string='Status')
        
    def action_export(self):
        book = xlwt.Workbook(encoding="utf-8")
        title = self._description

        sheet = book.add_sheet(title, cell_overwrite_ok=True)
        sheet.normal_magn = 80
        # sheet.show_grid = False

        style_header2 = xlwt.easyxf('font: name Calibri, height 310, bold 1; \
            pattern: pattern solid, fore_colour gray25;borders: left thin, \
            right thin, top thin, bottom thin;align: vert centre, horz center', num_format_str='#,##0.00')
        style_no_bold_left = xlwt.easyxf('font: name Calibri; align: vert centre, horz left')
        style_no_bold = xlwt.easyxf('font: name Calibri; align: vert centre, horz center')
        style_no_bold.num_format_str = '#,##0.00'

        batch_obj = self.env['batch.mrp.production']
        production_obj = self.env['mrp.production']
        sm_obj = self.env['stock.move']

        now = datetime.now()
        header = ['No', 'Tanggal', 'No OKP', 'BO number', 'BO code', 'Total batch', 'Total Goods', 'Reject', 'Sampling Qc Internal', 'Sampling Qc External', 'Item Code', 'Nama Produk', 'Lot No', 'No', 'Item Code PM',	'Nama RM', 'Lot', 'UOM', 'total usage BO']
        col_width = 256 * 25
        try:
            for i in itertools.count():
                sheet.col(i).width = col_width
                sheet.col(0).width = 256 * 6
                sheet.col(7).width = 256 * 40
                sheet.col(8).width = 256 * 60
                sheet.col(9).width = 256 * 60
                sheet.col(11).width = 256 * 40
                sheet.col(13).width = 256 * 6
                sheet.col(18).width = 256 * 60
        except ValueError:
            pass

        colh = -1
        for x in header:
            colh += 1
            style_header2.alignment.wrap = 1
            sheet.write(0, colh, x, style_header2)
            
        date_start_ori = self.date_from
        date_end_ori = self.date_to
        date_start = datetime(date_start_ori.year, date_start_ori.month, date_start_ori.day, 00, 00,00) - timedelta(hours=7) 
        date_end = datetime(date_end_ori.year, date_end_ori.month, date_end_ori.day, 23, 59, 59) - timedelta(hours=7) 
        # print(date_start,'XXX',date_end)
        domain = [('tipe', '=', self.report_type),
            ('actual_complete_date', '>=', date_start), 
            ('actual_complete_date', '<=', date_end)]
        if self.state != 'all':
            domain.append(('state', '=', self.state))
        data_dict = {}
        list_sm = []
        batch_ids = batch_obj.sudo().search(domain)
        production_ids = production_obj.sudo().search([('bache_id','in', batch_ids.ids),('state','!=','cancel')])
        for x in batch_ids:
            if x.okp_id not in data_dict:
                data_dict[x.okp_id] = {x:{}}
            else:
                data_dict[x.okp_id][x] = {}
        for mrp in production_ids:
            for line in mrp.move_raw_ids:
                list_sm.append(line.id)
        # stock_move = sm_obj.sudo().search([('raw_material_bache_id', 'in',batch_ids.ids),('state','=','done')])
        stock_move = sm_obj.sudo().browse(tuple(list_sm))
        for x in stock_move.filtered(lambda l: l.state == 'done'):
            batch = x.raw_material_production_id.bache_id
            okp = x.raw_material_production_id.bache_id.okp_id
            product = x.product_id
            if okp not in data_dict:
                data_dict[okp] = {batch : {product : {} } }
            else:
                if batch not in data_dict[okp]:
                    data_dict[okp][batch] = {product : {} }
                else:
                    if product not in data_dict[okp][batch]:
                        data_dict[okp][batch][product] = {}
            for rw in x.move_line_ids:
                if rw.lot_id.name not in data_dict[okp][batch][product]:
                    data_dict[okp][batch][product][rw.lot_id.name] = {rw.product_uom_id.name : [rw.qty_done]}
                else:
                    if rw.product_uom_id.name not in data_dict[okp][batch][product][rw.lot_id.name]:
                        data_dict[okp][batch][product][rw.lot_id.name][rw.product_uom_id.name] = [rw.qty_done]
                    else:
                        data_dict[okp][batch][product][rw.lot_id.name][rw.product_uom_id.name].append(rw.qty_done)
        no = 0
        num_1 = 0
        for k, v in data_dict.items():
            for batch, y in v.items():
                no += 1
                num_1 += 1
                sheet.write(no, 0, str(num_1), style_no_bold)
                sheet.write(no, 1, str(batch.date_okp), style_no_bold)
                sheet.write(no, 2, str(batch.okp_id.name or ' '), style_no_bold_left)
                sheet.write(no, 3, str(batch.number_bo or ''), style_no_bold)
                sheet.write(no, 4, str(batch.name), style_no_bold)
                sheet.write(no, 5, str(batch.batch_proses), style_no_bold)
                sheet.write(no, 6, str(batch.goods_qty), style_no_bold)
                sheet.write(no, 7, str(batch.reject_qty), style_no_bold)
                sheet.write(no, 8, str(batch.sampling_qty), style_no_bold)
                sheet.write(no, 9, str(batch.sampling_ex_qty), style_no_bold)
                sheet.write(no, 10, str(batch.product_id.default_code or ' '), style_no_bold_left)
                sheet.write(no, 11, str(batch.product_id.name or ' '), style_no_bold_left)
                lot_producing_id = ''
                if batch.mrp_line.filtered(lambda l : l.lot_producing_id):
                    lot_producing_id = batch.mrp_line[0].lot_producing_id.name
                sheet.write(no, 12, str(lot_producing_id or ''), style_no_bold_left)
                num_2 = 0
                for p, o in y.items():
                    num_2 += 1
                    sheet.write(no, 13, str(num_2), style_no_bold)
                    sheet.write(no, 14, str(p.default_code or ' '), style_no_bold_left)
                    sheet.write(no, 15, str(p.name or ' '), style_no_bold_left)
                    for w, h in o.items():
                        sheet.write(no, 16, str(w or ' '), style_no_bold_left)
                        for i, g in h.items():
                            sheet.write(no, 17, str(i or ' '), style_no_bold)
                            sheet.write(no, 18, sum(g), style_no_bold)
                            no += 1
        
        file_data = io.BytesIO()
        book.save(file_data)
        filename= '%s %s.xls' % (str(self.report_type), now)
        out = base64.encodestring(file_data.getvalue())
        self.write({'data_file': out, 'name': filename})

        view = self.env.ref('bmo_mrp_material.mrp_material_usage_report_form')
        return {
            'view_type': 'form',
            'views': [(view.id, 'form')],
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'mrp.material.usage',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
            
