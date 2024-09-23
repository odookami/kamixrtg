import io
import os
import base64
from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from odoo.exceptions import ValidationError
from odoo import api, fields, models, SUPERUSER_ID

class ReportSo(models.Model):
    _inherit = 'sale.order'
    _description = 'Report So'
    
    exported_file = fields.Binary(string='File')
    exported_file_name = fields.Char(string='Filename')


    def action_export(self):
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(PROJECT_ROOT)
        PATH_DIR = '/static/src/doc/'
        FILE_DIR = BASE_DIR + PATH_DIR
        for record in self:
            FILE_NAME = 'sales_order.xlsx'
            wb = load_workbook(FILE_DIR + FILE_NAME) 
            sheet = wb.active                

            row = 0
            for lines in record.order_line:
                product = lines.product_id.default_code
                qty = lines.qty_pcs
                do = lines.qty_delivered
                so_out = lines.product_uom_qty
                so_oustanding = so_out - do
                state = dict(record._fields['state'].selection).get(record.state)
                cell_line_dict = {
                    'A6': record.date_order.strftime('%d-%b-%Y'),
                    'B6': record.name,
                    'C6': record.partner_id.name,
                    'D6': record.partner_shipping_id.street,
                    'E6': product,
                    'F6': qty,
                    'G6': state,
                    'H6': do,
                    'I6': so_oustanding,
                }
                for key, value in cell_line_dict.items():
                    keys = key[0] + str(int(key[1:3]) + row)
                    sheet[keys] = value 
                row += 1

            file_data = io.BytesIO()
            wb.save(file_data)
            file_name = str(record.name) + '.xlsx'
            file_value = base64.encodebytes(file_data.getvalue())
            vals = {'exported_file_name': file_name, 'exported_file': file_value}
            record.with_user(SUPERUSER_ID).write(vals)

            model = record._name
            field_file = 'exported_file'
            content = 'web/content/?model=%s&field=%s' % (model, field_file)
            download = '&download=true&id=%s&filename=%s' % (record.id, file_name)
            url = content + download
            return {'type': 'ir.actions.act_url', 'url': url, 'target': 'new'}