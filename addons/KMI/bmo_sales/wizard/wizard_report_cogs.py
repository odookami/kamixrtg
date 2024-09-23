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
import pytz

class wizard_revisi(models.TransientModel):
    _name = "wizard.report.cogs"
    _description = "Report COGS"

    select_month = fields.Selection([
        ("01", "Januari"), 
        ("02", "Februari"), 
        ("03", "Maret"), 
        ("04", "April"),
        ("05", "Mei"),
        ("06", "Juni"),
        ("07", "Juli"),
        ("08", "Agustus"),
        ("09", "September"),
        ("10", "Oktober"),
        ("11", "Nopember"),
        ("12", "Desember"),], string='Month')
    select_year = fields.Selection(
        [(str(num), str(num)) for num in range(2020, (datetime.now().year)+2 )])
    data_file = fields.Binary('File')
    name = fields.Char('File Name')

    def export_excel(self):
        book = xlwt.Workbook(encoding="utf-8")
        title = self._description

        sheet = book.add_sheet(title, cell_overwrite_ok=True)
        sheet.normal_magn = 80
        sheet.show_grid = False

        style_no_bottom_border = xlwt.easyxf('font: name Calibri, height 360, \
            bold 1;align: horz center')
        style_bold_left = xlwt.easyxf('font: name Calibri, height 240, bold 1; \
            align: horz left')
        style_header2 = xlwt.easyxf('font: name Calibri, height 210, bold 1; \
            pattern: pattern solid;borders: left thin, \
            right thin, top thin, bottom thin;align: vert centre, horz center')
        style_no_bold = xlwt.easyxf('font: name Calibri, height 190; borders: \
            left thin, right thin, top thin, bottom thin;')
        style_no_bold.num_format_str = '#,##0.00'
        style_bold_center_tot = xlwt.easyxf('font: bold 1;''borders: left thin, \
            right thin, top thin, bottom thin;align: horz right; \
            pattern: pattern solid, fore_colour gray25;')
        style_bold_center_tot.num_format_str = '#,##0.00'

        now = datetime.now()
        judul = "COST OF GOOG SOLD REPORT"
        # judul = f'Report Dashboard {self.type_product}'
        header = ['Item Code', 'Item Description', 'Qty Sold', 'Net Sales']

        col_width = 256 * 25
        try:
            for i in itertools.count():
                sheet.col(i).width = col_width
                sheet.col(0).width = 256 * 25
                sheet.col(1).width = 256 * 40
                sheet.col(2).width = 256 * 20
                sheet.col(3).width = 256 * 40
        except ValueError:
            pass

        colh = -1
        for x in header:
            colh += 1
            style_header2.alignment.wrap = 1
            sheet.write(5, colh, x, style_header2)

        # no = 5;
        # for line in data_source:
        #     no += 1
        #     col = -1
        #     for i in header:
        #         sheet.row(no).height = 5 * 75
        #         sheet.row(no).height_mismatch = True
        #         col += 1
        #         sheet.write(no, col, line[i], style_no_bold)

        file_data = io.BytesIO()
        book.save(file_data)

        self.name = '%s %s.xls' % (judul, now)

        excel_file = base64.encodestring(file_data.getvalue())
        self.data_file = excel_file

        view = self.env.ref('bmo_sales.wizard_report_cogs_form_view')

        return {
            'view_type' : 'form',
            'views'     : [(view.id, 'form')],
            'view_mode' : 'form',
            'res_id'    : self.id,
            'res_model' : 'wizard.report.cogs',
            'type'      : 'ir.actions.act_window',
            'target'    : 'new',
        }
