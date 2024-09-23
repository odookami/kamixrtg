# -*- coding: utf-8 -*-

import io
import os
import base64
import pytz
from pytz import timezone
from dateutil.relativedelta import relativedelta
from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from odoo.exceptions import ValidationError, UserError
from odoo import api, fields, models, SUPERUSER_ID, _


class MRP_QC(models.Model):
    _name = 'mrp.qc'
    _description = 'MRP QC'

    name = fields.Char(
        'Name', default=lambda self: _('New'), copy=False, readonly=True)
    production_date = fields.Date(
        "Production Date")
    product_id = fields.Many2one(
        "product.product", "Item Description", domain="[('tipe_category','!=',False)]" )
    item_code = fields.Char(
        "Item Code", related="product_id.default_code")
    physcial_number = fields.Many2many(
        "master.sequence", 'physcial_number_tag', string="PHYSICAL")
    state_physcial = fields.Selection(
        [('Open','Open'),('On Progress','On Progress'),('Complete','Complete')], string="Status Physcial", compute="_check_data_class")
    chemical_number = fields.Many2many(
        "master.sequence", 'chemical_number_tag', string="CHEMICAL")
    state_chemical = fields.Selection(
        [('Open','Open'),('On Progress','On Progress'),('Complete','Complete')], string="Status Chemical", compute="_check_data_class")
    micro_number = fields.Many2many(
        "master.sequence", 'micro_number_tag', string="MICRO")
    state_micro = fields.Selection(
        [('Open','Open'),('On Progress','On Progress'),('Complete','Complete')], string="Status Micro", compute="_check_data_class")
    readonly_data = fields.Boolean(compute='_compute_readonly_physcial', string='Readonly')
    leader_check = fields.Boolean(string='Leader Check',)
    leader_need_check = fields.Boolean(string='Leader Need Check',compute='_compute_leader_need_check')
    master_qc_id = fields.Many2one('master.qc', string="Master Data")
    #Archieve
    active = fields.Boolean('Active', default=True)

    def _compute_leader_need_check(self):
        self.leader_need_check = True if self.state == 'done' and not self.leader_check else False

    def action_leader_check(self):
        self.write({'leader_check' : True})

    @api.depends('date_physical')
    def _compute_readonly_physcial(self):
        for rec in self:
            if rec.date_physical or rec.date_micro:
                rec.readonly_data = True
            else:
                rec.readonly_data = False

    number_batch_proses_id = fields.Many2one(
        'number.batch.proses', 'Batch Number')
    mo_id = fields.Many2one(
        "mrp.production", "Batch Number")
    tipe_category = fields.Many2one(
        "type.category", "Type Category", related="product_id.tipe_category")
    lot_producing_id = fields.Many2one(
        'stock.production.lot', string='Lot Number')
    batch_number = fields.Char("Batch Number")
    state = fields.Selection(
        [('draft','Draft'),('done','Done')], string="Status", default="draft")
    mrp_qc_lines = fields.One2many(
        'mrp.qc.line', 'qc_id', 'MRP QC Lines', copy=True)
    date = fields.Date(
        'Create Date', default=fields.Date.context_today, readonly=True)
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1), readonly=True)
    pic_physical = fields.Char(
        "PIC Physical/Chemical")
    pic_micro = fields.Char(
        "PIC  Micro")
    date_physical = fields.Date(
        "Physical/Chemical")
    date_micro = fields.Date(
        "Micro")
    note = fields.Text("Note")


    @api.depends('mrp_qc_lines.result_value')
    def _check_data_class(self):
        for rec in self:
            physcial_list = [line.result_value for line in rec.mrp_qc_lines if line.test_calss in ('PHYSICAL')]
            chemical_list = [line.result_value for line in rec.mrp_qc_lines if line.test_calss in ('CHEMICAL')]
            micro_list = [line.result_value for line in rec.mrp_qc_lines if line.test_calss in ('MICRO')]
            if physcial_list:
                state_physcial = 'Open'
                update_check = [u for u in physcial_list if u == False]
                update_check_false = [u for u in physcial_list if u != False]
                if update_check and update_check_false:
                   state_physcial = 'On Progress'
                if not update_check:
                    state_physcial = 'Complete'
            else:
                state_physcial = ''
            if chemical_list:
                state_chemical = 'Open'
                update_check = [u for u in chemical_list if u == False]
                update_check_false = [u for u in chemical_list if u != False]
                if update_check and update_check_false:
                   state_chemical = 'On Progress'
                if not update_check:
                    state_chemical = 'Complete'
            else:
                state_chemical = ''
            if micro_list:
                state_micro = 'Open'
                update_check = [u for u in micro_list if u == False]
                update_check_false = [u for u in micro_list if u != False]
                if update_check and update_check_false:
                   state_micro = 'On Progress'
                if not update_check:
                    state_micro = 'Complete'
            else:
                state_micro = ''
            rec.state_physcial = state_physcial
            rec.state_chemical = state_chemical
            rec.state_micro = state_micro

    @api.onchange('mo_id')
    def _onchange_mo_id(self):
        for rec in self:
            if rec.mo_id:
                rec.tipe_category = rec.mo_id.product_id.tipe_category.id
                rec.product_id = rec.mo_id.product_id.id

    @api.onchange('production_date','number_batch_proses_id','product_id')
    def _onchange_domain_batch_mrp(self):
        okp = []
        number = []
        for o in  self.env['kmi.dumping'].search([('date','=',self.production_date)]):
            okp.append(o.okp_id.id)
            number.append(o.mo_id.number_ref)
        okp = [x.okp_id.id for x in self.env['kmi.dumping'].search([('date','=',self.production_date)])]
        mrp_src = self.env['mrp.production'].search([('tipe','=','Banded'), ("okp_id","in", tuple(okp)),("state","!=","cancel"),('product_id','=',self.product_id.id)])
        return {'domain':{'number_batch_proses_id': [('mo_id','in',mrp_src.ids),('number','in',number)]}}
    
    @api.onchange('number_batch_proses_id')
    def _onchange_lot_producing_id(self):
        for rec in self:
            okp = rec.number_batch_proses_id.okp_id.id
            lot = [x.lot_producing_id.id for x in self.env['mrp.production'].search([('tipe','=','Filling'), ("okp_id","=", okp),("state","!=","cancel")])]
            return {'domain':{'lot_producing_id':[('id','in',tuple(lot))]}}
    
    @api.onchange('lot_producing_id')
    def _onchange_lot_update_line(self):
        for rec in self:
            if rec.lot_producing_id and rec.mrp_qc_lines:
                for line in rec.mrp_qc_lines:
                    line.update({'lot_producing_id' : rec.lot_producing_id.id})

    def _create_mrp_line(self, product_id, tipe_category, mo_id=False):
        physcial_number = self.physcial_number.ids
        chemical_number = self.chemical_number.ids
        micro_number = self.micro_number.ids
        obj_master_line = self.env['master.qc.line']
        master_sequence = self.env['master.sequence'].search([]).ids
        # master_sequence = self.env['master.sequence']
        data_obj = self.env['master.data.qc.line']
        data_dict = {}
        self.master_qc_id = False
        for rec in self:
            for x in range(1,len(master_sequence)+1):
                for line in obj_master_line.search([('master_id.tipe_category','=',tipe_category.id)]):
                    rec.name = line[0].master_id.name
                    rec.master_qc_id = line.master_id.id
                    for n in line.sequence_ids:
                        if x == n.number:
                            if n.id in physcial_number:
                                for u in line.master_data_qc_lines.filtered(lambda data : data.test_calss == 'PHYSICAL'):
                                    if x not in data_dict:
                                        data_dict[x] = [u]
                                    else:
                                        if u not in data_dict[x]:
                                            data_dict[x].append(u)
                            if n.id in chemical_number:
                                for u in line.master_data_qc_lines.filtered(lambda data : data.test_calss == 'CHEMICAL'):
                                    if x not in data_dict:
                                        data_dict[x] = [u]
                                    else:
                                        if u not in data_dict[x]:
                                            data_dict[x].append(u)
                            if n.id in micro_number:
                                for u in line.master_data_qc_lines.filtered(lambda data : data.test_calss == 'MICRO'):
                                    if x not in data_dict:
                                        data_dict[x] = [u]
                                    else:
                                        if u not in data_dict[x]:
                                            data_dict[x].append(u)
            list_line = []

            for k, v in data_dict.items():
                for i in v:
                    lines = {
                        'code'              : mo_id.mo_id.product_id.default_code or '',
                        # 'lot_producing_id'  : mo_id.mo_id.lot_producing_id.id,
                        'lot_producing_id'  : self.lot_producing_id.id,
                        'batch'             : f'{mo_id.number}/{k}',
                        'name'              : i.name,
                        'test_calss'        : i.test_calss,
                        'unit'              : i.unit,
                        'value_char'        : i.value_char,
                        'min_value_num'     : i.min_value_num,
                        'max_value_num'     : i.max_value_num
                    }
                    list_line += [(0, 0, lines)]
            rec.mrp_qc_lines = False
            rec.write({'mrp_qc_lines': list_line})
    def update_line(self):
        for rec in self:
            rec._create_mrp_line(rec.product_id, rec.tipe_category, rec.number_batch_proses_id)

    def action_done(self):
        data_list = []
        for rec in self:
            if not rec.pic_physical or not rec.pic_micro or not rec.date_physical or not rec.date_micro:
                raise UserError(_('Mohon isi semua field'))
            data_list = [line.id for line in rec.mrp_qc_lines if not line.result_value]
            if data_list:
                raise UserError(_('Mohon isi semua field Result Value di line'))
            if not data_list:
                rec.write({'state': 'done'})

    def action_submit(self):
        data_list = []
        for line in self.mrp_qc_lines:
            if line.result_value:
                data_list.append(line.id)
        if not data_list:
            self._create_mrp_line(self.product_id, self.tipe_category, self.number_batch_proses_id)

    def revisi_batch_line(self):
        for rec in self:
            for i in rec.mrp_qc_lines:
                hasil = i.batch.split('/')
                i.write({'batch' : f'{rec.number_batch_proses_id.number}/{hasil[1]}'})


    # ----------------------------------------------------------------------------
    # ORM Overrides
    # ----------------------------------------------------------------------------

    def write(self, vals):
        for rec in self:
            if rec.lot_producing_id and rec.mrp_qc_lines:
                for line in rec.mrp_qc_lines:
                    line.update({'lot_producing_id' : rec.lot_producing_id.id})
        return super(MRP_QC, self).write(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("You cannot delete This document."))
        return super(MRP_QC, self).unlink()

    # @api.model
    # def create(self, vals):
    # 	if vals.get('name', _('New')) == _('New'):
    # 		vals['name'] = self.env['ir.sequence'].next_by_code('mrp.qc')
    # 	return super(MRP_QC, self).create(vals)

    exported_file = fields.Binary(string='File')
    exported_file_name = fields.Char(string='Filename')

    def action_export(self):
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(PROJECT_ROOT)
        PATH_DIR = '/static/src/doc/'
        FILE_DIR = BASE_DIR + PATH_DIR
        for record in self:
            FILE_NAME = 'mrp_qc.xlsx'
            wb = load_workbook(FILE_DIR + FILE_NAME)
            sheet = wb.active

            cell_header_dict = {
                'B4' : f'FINISHED GOODS {record.product_id.tipe_category.name}',
                'B7': record.production_date,
                'B8': record.product_id.name,
                'B9': record.item_code,
                'B10': record.lot_producing_id.name or '',
                'B11': record.mo_id.number_ref,
                'B13': record.note or '',
                'C6': record.date_physical,
                'D6': f'MICRO: {record.date_micro}',
                'C12': record.pic_physical,
                'D12': record.pic_micro,
                'A13': record.note or '',
                'J1': f': {record.name}',
                'J2': ': ',
                'J3': ': 1/1',
                'J4': ': ',
            }

            for key, value in cell_header_dict.items():
                sheet[key] = value
            row = 0
            for line in record.mrp_qc_lines:
                cell_line_dict = {
                    'A15': line.code or '',
                    'B15': line.lot_producing_id.name or '',
                    'C15': line.batch or '',
                    'D15': str(line.name or ''),
                    'E15': str(line.test_calss or ''),
                    'F15': str(line.unit or ''),
                    'G15': str(line.value_char or ''),
                    'H15': str(line.min_value_num or ''),
                    'I15': str(line.max_value_num or ''),
                    'J15': str(line.result_value or ''),
                }
                for key, value in cell_line_dict.items():
                    keys = key[0] + str(int(key[1:3]) + row)
                    # print(keys, "###K###")
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

class MRP_QC_line(models.Model):
    _name = 'mrp.qc.line'
    _description = 'MRP QC'

    qc_id = fields.Many2one(
        'mrp.qc', 'MRP QC', required=True, ondelete='cascade')
    code = fields.Char("Item Code")
    lot_producing_id = fields.Many2one(
        'stock.production.lot', string='Lot Number')
    batch = fields.Char("Batch / Retort")
    name = fields.Char("Test Parameter")
    test_calss = fields.Selection(
        [("PHYSICAL","PHYSICAL"),("MICRO","MICRO"),("CHEMICAL","CHEMICAL")], string="Test Class")
    unit = fields.Char(
        "Test Unit")
    value_char = fields.Char(
        "Value Char")
    min_value_num = fields.Char(
        "Min Value Num")
    max_value_num = fields.Char(
        "Max Value Num")
    result_value = fields.Char(
        "Result Value")
    readonly_data = fields.Boolean(compute='_compute_readonly_physcial', string='Readonly')
    @api.depends('qc_id.date_physical','qc_id.date_micro','test_calss')
    def _compute_readonly_physcial(self):
        for rec in self:
            if rec.qc_id.date_physical and rec.test_calss in ('PHYSICAL','CHEMICAL'):
                rec.readonly_data = True
            elif rec.qc_id.date_micro and rec.test_calss in ('MICRO'):
                rec.readonly_data = True
            else:
                rec.readonly_data = False
    check_data = fields.Selection(
        [('No','No'),('Good','Good'),('Over','Over')], 'Chec Value', compute='_compute_check_value')

    @api.depends('result_value')
    def _compute_check_value(self):
        for o in self:
            if o.value_char and o.result_value:
                value_char = o.value_char.upper()
                result_value = o.result_value.upper()
                if value_char == result_value:
                    o.check_data = 'Good'
                else:
                    o.check_data = 'No'
            elif o.min_value_num and o.max_value_num and o.result_value:
                min_value_num = float(o.min_value_num)
                max_value_num = float(o.max_value_num)
                result_value = float(o.result_value)
                if result_value < min_value_num:
                    o.check_data = 'No'
                elif result_value >= min_value_num and result_value <= max_value_num:
                    o.check_data = 'Good'
                else:
                    o.check_data = 'Over'
            else:
                o.check_data = ''

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _create_qc(self, mo):
        qc = self.env['mrp.qc'].create({
            'mo_id'             : mo.id,
            'product_id'        : mo.product_id.id,
            'tipe_category'     : mo.product_id.tipe_category.id,
            'lot_producing_id'  : mo.lot_producing_id.id,
        })
        return qc