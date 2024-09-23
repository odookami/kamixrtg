import io
import re
import xlrd
import json
import time
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
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from openpyxl.utils import get_column_letter, column_index_from_string
from pytz import timezone
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

def compare(date):
    month, year = date.split('-')
    return (year, month_num[month])


class ReportMrpQcSummary(models.TransientModel):
    _name = 'mrp.qc.summary.wizard'
    _description = 'Mrp QC Summary Report'

    date_start = fields.Date('Date From')
    date_end = fields.Date('Date To')
    data_file = fields.Binary('File')
    name = fields.Char('File Name')

    # @api.onchange('date_start')
    # def _onchange_date_start(self):
    #     if self.date_start:
    #         self.date_end = self.date_start + relativedelta(months=12) - relativedelta(days=1)

    # def src_data_sql(self, date_start, date_end):
    #     where_period = "pl.start_date >= '%s' AND pl.start_date <= '%s 17:00:00'" % (datetime.date(date_start), datetime.date(date_end))
    #     sql_query = """
    #         select 
    #             p_move.type_portfolio_id as type_portfolio_id,
    #             pl.start_date as date,
    #             p_move.id AS portfolio_move_id
    #         from portfolio_move AS p_move
    #         LEFT JOIN tenancy_rent_schedule AS pl on p_move.planing_line_id = pl.id
    #         WHERE %s
    #         ORDER BY p_move.type_portfolio_id
    #     """% (where_period)
    #     self._cr.execute(sql_query)
    #     return self._cr.dictfetchall()

    def eksport_excel(self):
        list_sheet = []
        header = ["Item Description", "Item Code", "Lot Number", "Batch Number", "Physical Test", "Chemical Test","Micro Test"]
        # header = self.env['mrp.qc'].browse['product_id']
        start = datetime.strptime(str(self.date_start), '%Y-%m-%d')
        end = datetime.strptime(str(self.date_end), '%Y-%m-%d')
        delta = relativedelta(months=1)
        # while start <= end:
        #     list_sheet.append(start.strftime("%m-%Y"))
        #     header.append(start.strftime("%B-%y"))
        #     start += delta
        workbook = xlwt.Workbook(encoding="utf-8")
        header_style = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        font = xlwt.Font()
        fontP = xlwt.Font()
        font.bold = True
        font.height = 240
        font.colour_index = 2
        fontP.bold = True

        # Cell Color
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = 22

        header_style.font = fontP
        header_style.alignment = alignment
        header_style.pattern = pattern

        header_data = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        header_data.alignment = alignment

        total_value_style = xlwt.XFStyle()
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_RIGHT
        total_value_style.alignment = alignment
        total_value_style.font = fontP

        colh = 0
        worksheet = workbook.add_sheet("Summ")
        col_width = 256 * 25
        try:
            for i in itertools.count():
                worksheet.col(i).width = col_width
                worksheet.col(0).width = 256 * 90
                worksheet.col(1).width = 256 * 20
                worksheet.col(2).width = 256 * 20
                worksheet.col(3).width = 256 * 20
                worksheet.col(4).width = 256 * 20
                worksheet.col(5).width = 256 * 20
                worksheet.col(6).width = 256 * 20
        except ValueError:
            pass
        
        colh = -1
        for x in header:
            colh += 1
            worksheet.write(1, colh, x, header_style)
        
        results = self.env['mrp.qc'].search([])

        data = []
        for x in results:
            print(x.mo_id,'==========')
            product = x.product_id.name
            item_code = x.item_code
            lot = x.mo_id.lot_producing_id.name
            mo = x.mo_id.name
            physical = x.state_physcial
            chemical = x.state_chemical
            micro = x.state_micro
            data.append({
                'Item Description'  : product,
                'Item Code'         : item_code,
                'Lot Number'        : lot,
                'Batch Number'      : mo,
                'Physical Test'     : physical,
                'Chemical Test'     : chemical,
                'Micro Test'        : micro,
            })
           
        no = 1
        for line in data:
            no += 1
            col = -1
            for i in header:
                col += 1
                worksheet.write(no, col, line[i])
        

        file_data = io.BytesIO()
        workbook.save(file_data)
        self.write({
            'data_file': base64.encodestring(file_data.getvalue()),
            'name': 'KAMI - Report Mrp QC Summary.xls'
        })
        return {
            'name': 'KAMI - Report Mrp QC Summary',
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'target': 'new'
        }