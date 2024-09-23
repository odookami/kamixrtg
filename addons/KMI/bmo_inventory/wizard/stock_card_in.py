from dataclasses import Field
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
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class wizard_report_stock_in(models.TransientModel):
    _name = 'wizard.report.stock.in'
    _description = "Wizard Report Stock In"
    
    @api.model
    def _default_location_dest(self):
        if self.env.user.location_id:
            return self.env.user.location_id.ids
        else:
            return False

    date_start      = fields.Date('Date Start', required=True)
    date_end        = fields.Date('Date End', required=True)
    location_id	    = fields.Many2one('stock.location','Lokasi Gudang')
    location_dest_ids = fields.Many2many('stock.location', string='Lokasi Gudang', default=_default_location_dest)
    all_product 	= fields.Boolean("All Product")
    product_ids	    = fields.Many2many(comodel_name="product.product")
    data_file       = fields.Binary('File')
    name            = fields.Char('File Name')

    @api.onchange('all_product','id')
    def _onchange_(self):
        for rec in self:
            if rec.all_product:
                rec.product_ids = self.env['product.product'].search([]).ids
            if rec.all_product == False:
                rec.product_ids = False
            return {'domain':{'location_dest_ids':[('id','in',self.env.user.location_id.ids)]}}
    
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
        text_center = xlwt.easyxf('font:height 200; align: horiz center;'
                             "borders: top thin,left thin,right thin,bottom thin")
        style_bold_left = xlwt.easyxf('font: name Calibri, height 240, bold 1; \
            align: horz left')
        style_header2 = xlwt.easyxf('font: name Calibri, height 210, bold 1; \
            pattern: pattern solid, fore_colour yellow;borders: left thin, \
            right thin, top thin, bottom thin;align: vert centre, horz center')

        header = ["TANGGAL DATANG", "NO SJ SUPPLIER", "KODE ITEM", "NAMA ITEM", "NO LOT", "ED","QTY", "UOM", "NO BPB"]

        sheet.row(0).height = 256 * 2
        sheet.row(2).height = 256 + 64
        sheet.write_merge(0, 0, 0, len(header) - 1, "WAREHOUSE DEPARTMENT", style_no_bottom_border)
        sheet.write_merge(1, 1, 0, len(header) - 1, "KARTU STOCK RECEIPT", style_no_bottom_border)
        sheet.write_merge(3, 3, 0, 1, 'Tanggal / Periode', style_bold_left)
        date_start = datetime.strptime(str(self.date_start), '%Y-%m-%d')
        date_end = datetime.strptime(str(self.date_end), '%Y-%m-%d')
        sheet.write(3, 2, '%s - %s' % (date_start or '', date_end or ''), style_bold_left)
        sheet.row(3).height = 256 + 64

# -----------------------------------------------------------------------------------------------------------------------------
        date_start = (datetime.strptime(str(self.date_start), '%Y-%m-%d') - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S")
        locations = self.env["stock.location"].search(
            [("id", "child_of", self.location_dest_ids.ids)]
        )
        where_period = "picking.scheduled_date >= '%s' AND picking.scheduled_date <= '%s 17:00:00'" % (date_start, self.date_end)
        if len(locations) > 1:
            where_location = f'move.location_dest_id in {tuple(locations.ids)}'
        else:
            where_location = "move.location_dest_id = %s" % (locations.id)
        if len(self.product_ids) >1:
            where_product = f'move.product_id in {tuple(self.product_ids.ids)}'
        else:
            where_product = "move.product_id = %s" % (self.product_ids.id)
        sql = """
            SELECT 
                picking.scheduled_date as incoming_date,
                pp.default_code as product_code,
                pt.name as product_name,
                lot.name as lot_name,
                move_line.expiration_date as ed,
                SUM(move_line.qty_done) AS qty,
                uom.name as uom,
                picking.name as picking_name,
                picking.origin as no_bpb
            FROM stock_move move
                JOIN stock_move_line as move_line ON move.id = move_line.move_id
                LEFT JOIN stock_production_lot lot ON lot.id=move_line.lot_id
                LEFT JOIN uom_uom uom ON uom.id=move_line.product_uom_id
                LEFT JOIN product_product pp ON pp.id=move_line.product_id
                LEFT JOIN product_template pt ON pt.id=pp.product_tmpl_id
                JOIN stock_picking picking ON picking.id=move_line.picking_id
                JOIN stock_picking_type picking_type ON picking_type.id = picking.picking_type_id
            WHERE picking_type.code = 'incoming' and %s and %s and %s
            Group By
                picking.scheduled_date,
                pp.default_code,
                pt.name,
                lot.name,
                move_line.expiration_date,
                uom.name,
                picking.origin,
                picking.name
            ORDER BY picking.name
        """ % (where_period, where_location, where_product)
        self.env.cr.execute(sql)
        results = self.env.cr.dictfetchall()

        data = []
        for i in results:
            end = ''
            print(end)
            if i['ed']:
                date_ex = i['ed'] + timedelta(hours=7)
                end = date_ex.strftime("%Y-%m-%d")  
            data.append({
                'TANGGAL DATANG' : i['incoming_date'].strftime("%Y-%m-%d"),
                'NO SJ SUPPLIER' : i['no_bpb'],
                'KODE ITEM'   	 : i['product_code'],
                'NAMA ITEM'      : i['product_name'],
                'NO LOT' 	   	 : i['lot_name'],
                'ED'      	   	 : end,
                'QTY'          	 : i['qty'],
                'UOM'	   		 : i['uom'],
                'NO BPB' 		 : i['picking_name'],
            })

        col_width = 256 * 25
        try:
            for i in itertools.count():
                sheet.col(i).width = col_width
                # sheet.col(0).width = 256 * 5
                sheet.col(0).width = 256 * 20
                sheet.col(1).width = 256 * 22
                sheet.col(2).width = 256 * 22
                sheet.col(3).width = 256 * 25
                sheet.col(4).width = 256 * 20
                sheet.col(5).width = 256 * 20
                sheet.col(6).width = 256 * 30
                sheet.col(7).width = 256 * 30
                sheet.col(8).width = 256 * 30
        except ValueError:
            pass

# -----------------------------------------------------------------------------------------------------------------------------
        no = 7;
        for line in data:
            no += 1
            col = -1
            for i in header:
                sheet.row(no).height = 5 * 75
                sheet.row(no).height_mismatch = True
                col += 1
                sheet.write(no, col, line[i], text_left)

        colh = -1
        for x in header:
            colh += 1
            style_header2.alignment.wrap = 1
            sheet.write(7, colh, x, header_style)

        file_data = io.BytesIO()
        book.save(file_data)

        filename = 'KARTU_STOCK_RECEIPT.xls'

        out = base64.encodestring(file_data.getvalue())
        self.write({'data_file': out, 'name': filename})

        view = self.env.ref('bmo_inventory.form_wizard_report_stock_in')
        return {
            'view_type': 'form',
            'views': [(view.id, 'form')],
            'view_mode': 'form',
            'res_id': self.id,
            'res_model': 'wizard.report.stock.in',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }