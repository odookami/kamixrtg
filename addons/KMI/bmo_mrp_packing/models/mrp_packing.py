# -*- coding: utf-8 -*-

import io
import os
import base64
from datetime import timedelta
from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, SUPERUSER_ID

# class StockProductionLot(models.Model):
#     _inherit = 'stock.production.lot'

#     # * update expiration_date from related lot 
#     def write(self, values):
#         # Add code here
#         if 'expiration_date' in values:
#             bhp_obj = self.env['mrp.production.packing']
#             domain = [('lot_producing_id', '=', self.id)]
#             bhp_ids = bhp_obj.search(domain)
#             for bhp in bhp_ids:
#                 # * to fix mismatch hour, from UTC to GMT-7
#                 exp_date = fields.Datetime.from_string(values['expiration_date'])
#                 delta_exp_date = exp_date + relativedelta(hours=7)
#                 # * ---------------------------------------
#                 bhp.expiration_date = delta_exp_date
#         return super(StockProductionLot, self).write(values)

class MrpProductonPacking(models.Model):
    _name = 'mrp.production.packing'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Bukti Hasil Produksi Packing (OBOL)'

    # * Dok Info
    active = fields.Boolean(string='Active', default=True)
    name = fields.Char(string='Name', default='BHP/', tracking=True)
    doc_no = fields.Char(string='No. Dok', tracking=True)
    revision = fields.Char(string='Revisi', tracking=True)
    num_of_pages = fields.Char(string='Hal', tracking=True)
    date_doc = fields.Date(string='Tanggal', default=fields.Date.today())
    date = fields.Date(string='Date', 
        default=fields.Date.today(), tracking=True)
    team = fields.Selection(string='Team', selection=[('A', 'A'), 
        ('B', 'B'), ('C', 'C'), ('D', 'D')], tracking=True)
    line_machine = fields.Selection(string='Line', selection=[('A', 'A'), 
        ('B', 'B'), ('C', 'C')], tracking=True)
    packing_type = fields.Selection(string='Packing Type', selection=[\
        ('Filling', 'Filling'), ('Banded', 'Banded'),], 
        required=True, tracking=True)
    state = fields.Selection(string='State', selection=[('draft', 'Draft'), 
        ('in_progress', 'In Progress'), ('done', 'Done'), 
        ('cancel', 'Cancel')], default='draft', tracking=True)

    # * Transfer & Stock Move
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type')
    picking_id = fields.Many2one('stock.picking', string='Last Transfer', tracking=True)
    picking_id = fields.Many2many('stock.picking', string='Transfers', tracking=True)
    move_id = fields.Many2one('stock.move', string='Stock Move', tracking=True)
    location_dest_id = fields.Many2one('stock.location', string='Destination Location', tracking=True)
    location_src_id = fields.Many2one('stock.location', string='Source Location', tracking=True)
    
    # * OKP info
    okp_id = fields.Many2one('mrp.okp', string='No. OKP', 
        required=True, tracking=True)
    lot_producing_id = fields.Many2one('stock.production.lot', 
        'No. Lot', tracking=True)
    product_id = fields.Many2one('product.product', 
        string='Item Name', tracking=True)
    # expiration_date = fields.Date(string='Exp Date', tracking=True)
    expiration_date = fields.Datetime(related='lot_producing_id.expiration_date')
    date_okp = fields.Date(string='OKP Date', tracking=True)
    shift_okp = fields.Selection(string='Shift ', selection=[('I', 'I'), 
        ('II', 'II'), ('III', 'III')], tracking=True)
    batch_mrp_id = fields.Many2one('batch.mrp.production', string='Batch MRP')
    batch_mrp_ids = fields.Many2many('batch.mrp.production', string='Batch MRP ')
    
    def _get_batch_mrp(self, okp_id, packing_type):
        batch_mrp_obj = self.env['batch.mrp.production']
        # domain_batch = [('tipe', '=', packing_type), ('state', '!=', 'draft')]
        domain_batch = [('tipe', '=', packing_type), ('state', 'in', ['progress', 'done'])]
        if okp_id:
            domain_batch.append(('okp_id', '=', okp_id.id))
        batch_mrp_ids = batch_mrp_obj.search(domain_batch)
        return batch_mrp_ids

    okp_not_found = fields.Boolean(string='OKP is Not Found')
    
    @api.onchange('okp_id', 'product_id', 'lot_producing_id', 'packing_type', 'doc_no')
    def _onchange_okp_id(self):
        value = {}
        domain = {}
        batch_mrp_ids = self._get_batch_mrp(self.okp_id, self.packing_type)
        okp_ids = [x.okp_id.id for x in batch_mrp_ids]
        # value['okp_id'] = False if not okp_ids else okp_ids[0]
        domain = {} if not okp_ids else {'okp_id': [('id', 'in', okp_ids)]}
        if self.okp_id:
            batch_mrp_id = self._get_batch_mrp(self.okp_id, self.packing_type)
            if len(batch_mrp_id) > 1:
                batch_mrp_id = batch_mrp_id[0]
                raise ValidationError('OKP No %s dengan Tipe %s harusnya tidak lebih dari satu' % (self.okp_id.name, self.packing_type))
            
            lot_ids = [x.lot_producing_id.id for x in batch_mrp_id.mrp_line \
                if x.lot_producing_id and x.tipe == self.packing_type] if batch_mrp_id else []

            value['date_okp'] = False if not batch_mrp_id else batch_mrp_id.date_okp
            # value['expiration_date'] = False if not self.lot_producing_id \
            #     else self.lot_producing_id.expiration_date
            value['product_id'] = False if not batch_mrp_id else batch_mrp_id.product_id.id
            domain = {} if not batch_mrp_id else {'product_id': [('id', '=', batch_mrp_id.product_id.id)]}

            value['lot_producing_id'] = False if not lot_ids else lot_ids[0]
            domain = {} if not lot_ids else {'lot_producing_id': [('id', 'in', lot_ids)]}

            value['batch_mrp_id'] = False if not batch_mrp_id else batch_mrp_id.id
            location_src_id = [x.location_dest_id.id for x in batch_mrp_id.mrp_line]
            value['location_src_id'] = False if not location_src_id else location_src_id[0]
            picking_type_id = [x.picking_type_id.id for x in batch_mrp_id.mrp_line]
            value['picking_type_id'] = False if not picking_type_id else picking_type_id[0]
            value['location_dest_id'] = self._get_dest_id()
            # print(value, "###V###")
        value['okp_not_found'] = True if not okp_ids else False
        # value['batch_mrp_ids'] = False if not batch_mrp_ids else [(6, 0, batch_mrp_ids.ids)]
        return {'value': value, 'domain': domain}

    def _get_dest_id(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        location_dest_id = int(get_param('bmo_mrp_packing.bhp_location_dest_id'))
        return location_dest_id

    def action_post(self):
        # for record in self:
        #     record.action_release()
        return self.write({'state': 'in_progress'})

    def action_done(self):
        return self.write({'state': 'done'})

    def action_cancel(self):
        return self.write({'state': 'cancel'})

    def action_draft(self):
        return self.write({'state': 'draft'})

    @api.model
    def create(self, vals):
        # Add code here
        seq_dict = {'Filling': 'bhp.pack.seq', 'Banded': 'bhp.banded.seq'}
        code = seq_dict[vals['packing_type']]
        name = self.env['ir.sequence'].next_by_code(code)

        doc_dict = {'Filling': 'FRM-PRD-120', 'Banded': 'FRM-PRD-122'}
        doc_no = False if not vals['packing_type'] else doc_dict[vals['packing_type']]

        vals.update({'name': name, 'doc_no': doc_no})
        return super(MrpProductonPacking, self).create(vals)

    def write(self, vals):
        # Add code here
        if 'mrp_packing_line' in vals:
            vals['state'] = 'in_progress'
            # print(vals['mrp_packing_line'], "###V###")
        return super(MrpProductonPacking, self).write(vals)
    
    def unlink(self):
        # Add code here
        for record in self:
            if record.state != 'draft':
                raise ValidationError('Hanya bisa menghapus data dengan status draft !')
        return super(MrpProductonPacking, self).unlink()
    
    exported_file = fields.Binary(string='File')
    exported_file_name = fields.Char(string='Filename')

    def set_border(self, sheet, cell_range):
        thin = Side(border_style="thin", color="000000")
        for row in sheet[cell_range]:
            for cell in row:
                cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

    def action_export(self):
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(PROJECT_ROOT)
        PATH_DIR = '/static/src/doc/'
        FILE_DIR = BASE_DIR + PATH_DIR
        for record in self:
            # record.set_border(sheet, 'A1:C4')
            FILE_NAME = 'pack.xlsx'
            if record.packing_type == 'Banded':
                FILE_NAME = 'banded.xlsx'
            wb = load_workbook(FILE_DIR + FILE_NAME) 
            sheet = wb.active
            
            expire_date = record.expiration_date + timedelta(hours=7)
            cell_header_dict = {
                'B5': record.okp_id.name,
                'B6': record.lot_producing_id.name,
                'D5': record.product_id.name,
                'D6': False if not expire_date else expire_date.strftime('%d-%m-%Y'),
                'L5': False if not record.date_okp else record.date_okp.strftime('%d-%m-%Y'),
                'L6': record.shift_okp,
                'P1': record.doc_no,
                'P2': False if not record.date else record.date.strftime('%d-%m-%Y'),
                # 'P3': record.num_of_pages,
                # 'P4': record.revision,
                'P5': record.line_machine,
                'P6': record.team,
            }
            
            for key, value in cell_header_dict.items():
                sheet[key].value = value 
            row = 0
            for line in record.mrp_packing_line:
                qty_done = 0
                move_ids = line.picking_id.move_ids_without_package
                # print(move_ids, "###move_ids###")
                for move in move_ids:
                    # for move_line in move.move_line_ids:
                    for move_line in move.move_line_ids.filtered(lambda x: x.result_package_id.name == line.package_id.name):
                        qty_done += move_line.qty_done
                    # print(qty_done, "###qty_done1###")
                # print(qty_done, "###qty_done2###")
                realesed = 'Release' if line.picking_id else ' '
                # print(line.picking_id, "###picking_id###")
                cell_line_dict = {
                    'B10': line.package_id.name,
                    'C10': line.start,
                    'D10': line.finish,
                    'E10': line.first_check_code if record.packing_type == 'Filling' else line.qty_in_ct,
                    'F10': line.first_check_time if record.packing_type == 'Filling' else line.qty_in_pcs,
                    'G10': line.first_check_count if record.packing_type == 'Filling' else line.total_output,
                    'H10': line.middle_check_code if record.packing_type == 'Filling' else line.qty_banded_in_ct,
                    'I10': line.middle_check_time if record.packing_type == 'Filling' else line.qty_banded_in_pcs,
                    'J10': line.middle_check_count if record.packing_type == 'Filling' else line.total_output_banded,
                    'K10': line.qty_in_ct if record.packing_type == 'Filling' else str(line.user_mrp or ' '),
                    'L10': line.qty_in_pcs if record.packing_type == 'Filling' else realesed,
                    'M10': line.total_output if record.packing_type == 'Filling' else str(line.user_whs or ' '),
                    'N10': str(line.user_mrp or ' ') if record.packing_type == 'Filling' else str(line.history or ' '),
                    'O10': realesed if record.packing_type == 'Filling' else ' ',
                    'P10': str(line.user_whs or ' ') if record.packing_type == 'Filling' else str(qty_done or ' '),
                    'Q10': str(line.history or ' ') if record.packing_type == 'Filling' else str(line.location_dest_id.name or ' '),
                    'R10': str(qty_done or ' ') if record.packing_type == 'Filling' else ' ',
                    'S10': str(line.location_dest_id.name or '') if record.packing_type == 'Filling' else ' ',
                }
                # print(cell_line_dict, "###cell_line_dict###")
                for key, value in cell_line_dict.items():
                    keys = key[0] + str(int(key[1:3]) + row)
                    # print(keys, "###K###")
                    if not isinstance(sheet[keys], tuple):
                        print(keys, sheet[keys], "###SK###", type(sheet[keys]))
                        sheet[keys].value = value 
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
            