import time
import tempfile
import binascii
import itertools
import xlrd
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning, ValidationError, UserError
from odoo import models, fields, exceptions, api,_
from dateutil.relativedelta import *
import io
import logging
_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')


class ImportMrpKAMI(models.TransientModel):
    _name = 'import.mrp.kami'
    _description = 'Import MRP'

    file_data = fields.Binary('File')
    file_name = fields.Char('File Name')
    
    def import_budget(self):
        if not self.file_name:
            raise ValidationError(_('Unselected file'))
        
        fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.file_data))
        fp.seek(0)

        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        obj_import = self.env["mrp.production"]
        active_id = self.env.context.get('active_id')
        cs_obj = obj_import.browse(active_id)
        quant = self.env['stock.quant']

        cont = -1
        for row_no in range(sheet.nrows):
            cont += 1
            date_year = False
            if row_no <= 0:
                fields = map(lambda row:row.value.encode('utf-8'), sheet.row(row_no))
            else:
                line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                
                if line[0]:
                    mrp_src = obj_import.browse(int(float(line[0]))).filtered(lambda l: l.state in ('draft','confirmed','progress','to_close'))
                    if not mrp_src:
                        raise ValidationError(_(f'line {cont} MO {line[0]} Tidak di temukan atau status harus draft atau confirmed'))
                    for mo in mrp_src:
                        for move in mo.move_raw_ids.filtered(lambda l: l.product_id.default_code == line[1]):
                            quant_obj = quant.search([
                                ('product_id.default_code','=', str(line[1])),('location_id', '=', move.location_id.id), ('lot_id.name', '=', str(line[2]))], limit=1)
                            if not quant_obj:
                                raise ValidationError(_(f'LOT {line[2]} Tidak di temukan'))
                            qty_done_move_line = move._update_reserved_quantity_manual_kmi(
                                float(line[3]), 
                                float(line[3]), 
                                quant_obj.location_id, 
                                lot_id=quant_obj.lot_id, 
                                package_id=quant_obj.package_id, 
                                quant=quant_obj, 
                                strict=True)
                            if move.product_id.uom_id.id != move.product_uom.id:
                                qty_done_move_line = move.product_id.uom_id._compute_quantity(qty_done_move_line, move.product_uom, rounding_method='HALF-UP')
                            product_uom_qty = move.product_uom_qty + qty_done_move_line
                            move.write({'product_uom_qty' : product_uom_qty})