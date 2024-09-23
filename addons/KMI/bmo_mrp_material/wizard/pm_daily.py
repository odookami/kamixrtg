# -*- coding: utf-8 -*-

import io
import pytz
import base64
import itertools
import pandas as pd
from odoo.tools.misc import xlwt
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


IDM = {
    '01': 'Januari', '02': 'Februari', '03': 'Maret',
    '04': 'April', '05': 'Mei', '06': 'Juni', 
    '07': 'Juli', '08': 'Agustus', '09': 'September', 
    '10': 'Oktober', '11': 'Nopember', '12': 'Desember',
}
# data configurasi
categ_xml_id = 'bmo_mrp_material.pm_categ_id'
rtw_loc_xml_id = 'bmo_mrp_material.return_loc_id'
rtw_dest_xml_id = 'bmo_mrp_material.return_dest_id'
gain_loc_xml_id = 'bmo_mrp_material.gain_loc_id'
gain_dest_xml_id = 'bmo_mrp_material.gain_dest_id'

def _value_disct(product_id, produk_uom_id, uom_id, lot_id, qty_awal, okp, okp_in, okp_out, shift, fs_manual, bottle_out, out_qty, reject, total_out, reject_out, qty, number_bo, qty_done, product_qty, product_in, product_out, return_qty):
    return {
        'product_id': product_id, 
        'produk_uom_id': produk_uom_id, 
        'uom_id': uom_id, 
        'lot_id':lot_id, 
        'qty_awal':qty_awal,
        'okp': okp, 
        'okp_in': okp_in, 
        'okp_out': okp_out, 
        'shift': shift, 
        'fs_manual':fs_manual, 
        'bottle_out':bottle_out, 
        'out_qty': out_qty, 
        'reject': reject, 
        'total_out': total_out, 
        'reject_out': reject_out, 
        'qty': qty, 
        'number_bo': number_bo, 
        'qty_done': qty_done, 
        'product_qty': product_qty, 
        'product_in': product_in, 
        'product_out': product_out,
        'return_qty' : return_qty,
    }

class MrpPmDailyReport(models.TransientModel):
    _name = 'mrp.pm.daily.report'
    _description = 'Report PM Harian'

    tipe = fields.Selection([('all', 'ALL'), ('dep', 'Department')], 
        string='Tipe Report', default='all', required=True)
    user_id = fields.Many2one('res.users','Created By', required=True, \
        readonly=True, default=lambda self: self.env.uid)
    department_id = fields.Many2one('hr.department', 'Departement')
    state = fields.Selection([('all', 'All Status'), ('draft', 'Draft'), 
        ('verify', 'Waiting'), ('done', 'Done'), ('cancel', 'Rejected')], 
        string='Status', default='draft', required=True)
    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    data_file = fields.Binary('File')
    name = fields.Char('File Name')
    adv_filter = fields.Boolean(string='Advance Filter')
    employee_ids = fields.Many2many('hr.employee', string='Employee')
    analytic_ids = fields.Many2many('account.analytic.account', string='Site Card')

    @api.constrains('date_from', 'date_to')
    def _check_date_from(self):
        if ((self.date_to - self.date_from).days + 1) > 7:
            raise UserError(_('Periode tidak boleh lebih dari 7 hari !'))

    def _get_params(self, xml_id):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        result = int(get_param(xml_id))
        return result
    
    def _get_data_dict(self, data_sql_dict, list_okp, header_shift, list_out_okp):
        data_dict = {}
        for v in data_sql_dict['awal']:
            product_id = v['product_id']
            product_src = self.env['product.product'].browse(product_id)
            produk_uom_id = self.env['uom.uom'].browse(v['produk_uom_id'])
            uom_id = self.env['uom.uom'].browse(v['uom_id'])
            lot_name = v['lot_id']
            okp_src = self.env['batch.mrp.production'].browse(v['okp'])
            okp_name = okp_src.okp_id.name if okp_src else 'Kosong'
            
            qty_awal = v['qty_awal']
            hasil_qty_okp = v['okp_in'] - v['okp_out']

            shift = v['shift']
            fs_manual = v['fs_manual'] if v['fs_manual'] else 0

            bottle_out = v['bottle_out'] if v['bottle_out'] else 0

            out_qty = v['out_qty'] if v['out_qty'] else 0
            reject = v['reject'] if v['reject'] else 0
            qty_filling = out_qty + reject

            total_out = v['total_out'] if v['total_out'] else 0
            reject_out = v['reject_out'] if v['reject_out'] else 0
            qty_banded = total_out + reject_out

            qty = v['qty'] if v['qty'] else 0

            number_bo = v['number_bo']
            product_out_okp = v['qty_done']

            product_qty = v['product_qty'] if v['product_qty'] else 0

            product_in = v['product_in']
            product_out = v['product_out']
            qty_gain_or_loss = product_in - product_out
            qty_gain_or_loss = abs(qty_gain_or_loss) if qty_gain_or_loss < 0 else -qty_gain_or_loss
            
            return_qty = v['return_qty']

            if produk_uom_id.id != uom_id.id:
                qty_awal = uom_id._compute_quantity(qty_awal, produk_uom_id)
                hasil_qty_okp = uom_id._compute_quantity(hasil_qty_okp, produk_uom_id)
                fs_manual = uom_id._compute_quantity(fs_manual, produk_uom_id)
                bottle_out = uom_id._compute_quantity(bottle_out, produk_uom_id)
                qty_filling = uom_id._compute_quantity(qty_filling, produk_uom_id)
                qty_banded = uom_id._compute_quantity(qty_banded, produk_uom_id)
                qty = uom_id._compute_quantity(qty, produk_uom_id)
                product_out_okp = uom_id._compute_quantity(product_out_okp, produk_uom_id)
                product_qty = uom_id._compute_quantity(product_qty, produk_uom_id)
                qty_gain_or_loss = uom_id._compute_quantity(qty_gain_or_loss, produk_uom_id)
                return_qty = uom_id._compute_quantity(return_qty, produk_uom_id)

            nilai_positif = qty_awal + hasil_qty_okp
            nilai_negatig = abs(product_out_okp) + abs(product_qty) + return_qty + qty_gain_or_loss
            qty_akhir = nilai_positif - nilai_negatig
            if product_id not in data_dict:
                data_dict[product_id] = {lot_name : {'lot' : [qty_akhir], 'okp' : {}, 'shift' : {}, 'out_bo' : {}, 'reject' : [0], 'return' : [0], 'gain_or_loss' : [0], 'sisa' : [0]}}
            else:
                if lot_name not in data_dict[product_id]:
                    data_dict[product_id][lot_name] = {'lot' : [qty_akhir], 'okp' : {}, 'shift' : {}, 'out_bo' : {}, 'reject' : [0], 'return' : [0], 'gain_or_loss' : [0], 'sisa' : [0]}
                else:
                    if 'lot' not in data_dict[product_id][lot_name]:
                        data_dict[product_id][lot_name]['lot'] = [qty_akhir]
                    else:
                        data_dict[product_id][lot_name]['lot'].append(qty_akhir)

        for v in data_sql_dict['Data']:
            product_id = v['product_id']
            product_src = self.env['product.product'].browse(product_id)
            produk_uom_id = self.env['uom.uom'].browse(v['produk_uom_id'])
            uom_id = self.env['uom.uom'].browse(v['uom_id'])
            lot_name = v['lot_id']
            okp_src = self.env['batch.mrp.production'].browse(v['okp'])
            okp_name = okp_src.okp_id.name if okp_src else 'Kosong'
            
            hasil_qty_okp = v['okp_in'] - v['okp_out']

            shift = v['shift']
            fs_manual = v['fs_manual'] if v['fs_manual'] else 0

            bottle_out = v['bottle_out'] if v['bottle_out'] else 0

            out_qty = v['out_qty'] if v['out_qty'] else 0
            reject = v['reject'] if v['reject'] else 0
            qty_filling = out_qty + reject

            total_out = v['total_out'] if v['total_out'] else 0
            reject_out = v['reject_out'] if v['reject_out'] else 0
            qty_banded = total_out + reject_out

            qty = v['qty'] if v['qty'] else 0

            number_bo = v['number_bo']
            product_out_okp = v['qty_done']

            product_qty = v['product_qty'] if v['product_qty'] else 0

            product_in = v['product_in']
            product_out = v['product_out']
            qty_akhir = product_in - product_out
            return_qty = v['return_qty']

            if produk_uom_id.id != uom_id.id:
                hasil_qty_okp = uom_id._compute_quantity(hasil_qty_okp, produk_uom_id)
                fs_manual = uom_id._compute_quantity(fs_manual, produk_uom_id)
                bottle_out = uom_id._compute_quantity(bottle_out, produk_uom_id)
                qty_filling = uom_id._compute_quantity(qty_filling, produk_uom_id)
                qty_banded = uom_id._compute_quantity(qty_banded, produk_uom_id)
                qty = uom_id._compute_quantity(qty, produk_uom_id)
                product_out_okp = uom_id._compute_quantity(product_out_okp, produk_uom_id)
                product_qty = uom_id._compute_quantity(product_qty, produk_uom_id)
                qty_akhir = uom_id._compute_quantity(qty_akhir, produk_uom_id)
                return_qty = uom_id._compute_quantity(return_qty, produk_uom_id)

            qty_shift = fs_manual + bottle_out + qty_filling + qty_banded + qty
            if product_id not in data_dict:
                data_dict[product_id] = {
                    lot_name : {
                        'lot' : [0], 
                        'okp' : {okp_name : [hasil_qty_okp]}, 
                        'shift' : {shift : [qty_shift]}, 
                        'out_bo' : {number_bo : [product_out_okp]}, 
                        'reject' : [product_qty], 
                        'return' : [return_qty],
                        'gain_or_loss' : [qty_akhir], 
                        'sisa' : [0]
                    }
                }
            else:
                if lot_name not in data_dict[product_id]:
                    data_dict[product_id][lot_name] = {
                                                        'lot' : [0], 
                                                        'okp' : {okp_name : [hasil_qty_okp]}, 
                                                        'shift' : {shift : [qty_shift]}, 
                                                        'out_bo' : {number_bo : [product_out_okp]}, 
                                                        'reject' : [product_qty],
                                                        'return' : [return_qty],
                                                        'gain_or_loss' : [qty_akhir], 
                                                        'sisa' : [0]
                                                    }
                else:
                    data_dict[product_id][lot_name]['reject'].append(product_qty)
                    data_dict[product_id][lot_name]['return'].append(return_qty)
                    data_dict[product_id][lot_name]['gain_or_loss'].append(qty_akhir)

                    if 'okp' not in data_dict[product_id][lot_name]:
                        data_dict[product_id][lot_name]['okp'] = {okp_name : [hasil_qty_okp]}
                    else:
                        if okp_name not in data_dict[product_id][lot_name]['okp']:
                            data_dict[product_id][lot_name]['okp'][okp_name] = [hasil_qty_okp]
                        else:
                            data_dict[product_id][lot_name]['okp'][okp_name].append(hasil_qty_okp)

                    if 'shift' not in data_dict[product_id][lot_name]:
                        data_dict[product_id][lot_name]['shift'] = {shift : [qty_shift]}
                    else:
                        if shift not in data_dict[product_id][lot_name]['shift']:
                            data_dict[product_id][lot_name]['shift'][shift] = [qty_shift]
                        else:
                            data_dict[product_id][lot_name]['shift'][shift].append(qty_shift)

                    if 'out_bo' not in data_dict[product_id][lot_name]:
                        data_dict[product_id][lot_name]['out_bo'] = {number_bo : [product_out_okp]}
                    else:
                        if number_bo not in data_dict[product_id][lot_name]['out_bo']:
                            data_dict[product_id][lot_name]['out_bo'][number_bo] = [product_out_okp]
                        else:
                            data_dict[product_id][lot_name]['out_bo'][number_bo].append(product_out_okp)

        for k, v in data_dict.items():
            for i, x in v.items():
                for okp in list_okp:
                    if okp not in x['okp']:
                        x['okp'][okp] = [0]
                for shift in header_shift:
                    if shift not in x['shift']:
                        x['shift'][shift] = [0]
                for number_bo in list_out_okp:
                    if number_bo not in x['out_bo']:
                        x['out_bo'][number_bo] = [0]
                if 'Kosong' in x['okp']:
                    del x['okp']['Kosong']
                if False in x['out_bo']:
                    if sum(x['out_bo'][False]) == 0:
                        del x['out_bo'][False]
                if 'Kosong' in x['shift']:
                    del x['shift']['Kosong']
                if 'Kosong' in x['out_bo']:
                    del x['out_bo']['Kosong']
        return data_dict

    def _get_stock_awal(self, pm_config, update_date):
        pm_conf_src = pm_config
        categ_id = self._get_params(categ_xml_id)
        rtw_loc_id = self._get_params(rtw_loc_xml_id)
        rtw_dest_id = self._get_params(rtw_dest_xml_id)

        gain_loc_id = self._get_params(gain_loc_xml_id)
        gain_dest_id = self._get_params(gain_dest_xml_id)

        date_from = pm_conf_src.date
        datetime_from = date_from.strftime("%Y-%m-%d 17:00:00")

        if date_from == update_date.date():
            date_to = update_date.date()
        else:
            date_to = update_date.date() - relativedelta(days=1)
        datetime_to = date_to.strftime("%Y-%m-%d 17:00:00")

        obj_move_line  = self.env['stock.move.line']
        obj_labeling = self.env['kmi.labeling']
        obj_unscramble = self.env['kmi.unscramble']
        obj_filling = self.env['kmi.filling']
        obj_banded = self.env['banded.usage']
        obj_packing = self.env['kmi.packing']
        obj_batch_mrp = self.env['batch.mrp.production']
        obj_mrp_unbuild = self.env['mrp.unbuild']
        obj_stock_inventory = self.env['stock.inventory']

        data = []
        domain_categ_id = ('product_id.categ_id','=',categ_id)
        pm_conf_src = pm_config.conf_line.filtered(lambda l: l.product_id.categ_id.id == categ_id)
        for x in pm_conf_src:
            data.append(
                _value_disct(
                    product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, uom_id = x.product_id.uom_id.id, lot_id = x.lot_id.name, qty_awal = x.qty,
                    okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                    reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
            )
        # =============================OKP IN==================================================
        src_in_okp = obj_move_line.search([
            ('state', '=', 'done'), domain_categ_id,('date','>', datetime_from),('date','<', datetime_to)
        ])
        for x in src_in_okp:
            if x.move_id.picking_id.batch_production_id:
                okp = False if not x.move_id.picking_id.batch_production_id else x.move_id.picking_id.batch_production_id.id
                okp_in = okp_out = 0
                if x.location_dest_id.id == rtw_loc_id:
                    okp_in = x.qty_done
                if x.location_id.id == rtw_loc_id:
                    okp_out = x.qty_done
                data.append(
                    _value_disct(
                        product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, 
                        uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                        okp = okp, okp_in = okp_in, okp_out = okp_out, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                        reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                )
        # =============================LABELING==================================================
        src_labeling = obj_labeling.search([('state','not in', ('cancel','model','draft_model')), ('product_labeling_id.categ_id','=',categ_id), ('date','>', date_from),('date','<', date_to)])
        for x in src_labeling:
            for i in self.env['kmi.labeling.material.usage'].search([('labeling_id','=',x.id)]):
                data.append(
                    _value_disct(
                        product_id = x.product_labeling_id.id, produk_uom_id = x.product_labeling_id.uom_id.id, 
                        uom_id = x.product_labeling_id.uom_id.id, lot_id = i.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = x.shift, fs_manual = i.fs_manual, bottle_out = 0, out_qty = 0, 
                        reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                )
        # =============================Unscramble==================================================
        src_unscramble = obj_unscramble.search([('state','not in', ('cancel','model','draft_model')), ('product_silo_id.categ_id','=',categ_id), ('date','>', date_from),('date','<', date_to)])
        for x in src_unscramble:
            for i in self.env['kmi.unscramble.bottle.line'].search([('unscramble_id','=',x.id)]):
                data.append(
                    _value_disct(
                        product_id = x.product_silo_id.id, produk_uom_id = x.product_silo_id.uom_id.id, 
                        uom_id = x.product_silo_id.uom_id.id, lot_id = i.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = x.shift, fs_manual = 0, bottle_out = i.bottle_out, out_qty = 0, 
                        reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                )
        # =============================Filling Machine==================================================
        src_filling = obj_filling.search([('state','not in', ('cancel','model','draft_model')),('product_filling_id.categ_id','=',categ_id), ('date','>', date_from),('date','<', date_to)])
        for x in src_filling:
            for i in self.env['kmi.filling.material.usage'].search([('filling_daily_report_id','=',x.id)]):
                data.append(
                    _value_disct(
                        product_id = x.product_filling_id.id, produk_uom_id = x.product_filling_id.uom_id.id, 
                        uom_id = x.product_filling_id.uom_id.id, lot_id = i.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = x.shift, fs_manual = 0, bottle_out = 0, out_qty = i.out_qty, reject = i.reject, 
                        total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                )
        # =============================Stock Card Banded==================================================
        src_banded_usage = self.env['banded.usage'].search([('state','=', 'done'), ('date','>', date_from),('date','<', date_to)])
        for banded in src_banded_usage:
            for x in banded.material_usage_line_1.filtered(lambda l: l.item_id.categ_id.id == categ_id):
                data.append(
                    _value_disct(
                        product_id = x.item_id.id, produk_uom_id = x.item_id.uom_id.id, 
                        uom_id = x.item_id.uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = x.banded_usage_id.shift, fs_manual = 0, bottle_out = 0, out_qty = 0, reject = 0, 
                        total_out = x.out, reject_out = x.reject, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                )
            for x in banded.material_usage_line_2.filtered(lambda l: l.item_id.categ_id.id == categ_id):
                data.append(
                    _value_disct(
                        product_id = x.item_id.id, produk_uom_id = x.item_id.uom_id.id, 
                        uom_id = x.item_id.uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = x.banded_usage_id.shift, fs_manual = 0, bottle_out = 0, out_qty = 0, reject = 0, 
                        total_out = x.out, reject_out = x.reject, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                )
        # =============================Packing==================================================
        src_packing = obj_packing.search([('state','not in', ('cancel','model','draft_model')), ('product_packing_id.categ_id','=',categ_id), ('date','>', date_from),('date','<', date_to)])
        for x in src_packing:
            for i in self.env['kmi.packing.material.usage'].search([('packing_id','=',x.id)]):
                qty = i.out_qty + i.sample_qc + i.reject_machine_qty + i.reject_coding_qty + i.reject_supplier_qty
                data.append(
                    _value_disct(
                        product_id = x.product_packing_id.id, produk_uom_id = x.product_packing_id.uom_id.id, 
                        uom_id = x.product_packing_id.uom_id.id, lot_id = i.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = x.shift, fs_manual = 0, bottle_out = 0, out_qty = 0, reject =0, 
                        total_out = 0, reject_out = 0, qty = qty, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                )
        # =============================OKP OUT==================================================
        okp_src = self.env['batch.mrp.production'].search([('actual_closing','>', datetime_from),('actual_closing','<', datetime_to)])
        for okp in okp_src:
            for mo in okp.mrp_line:
                for move in mo.move_raw_ids:
                    for x in move.move_line_ids:
                        number_bo = okp.number_bo
                        qty_done = x.qty_done
                        data.append(
                            _value_disct(
                                product_id = move.product_id.id, produk_uom_id = move.product_id.uom_id.id, 
                                uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                                okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                                reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = number_bo, qty_done = qty_done, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                        )
        # =============================Reject==================================================
        srcmrp_unbuild = obj_mrp_unbuild.search([('state', '=', 'done'), domain_categ_id, ('create_date','>', datetime_from), ('create_date','<', datetime_to)])
        for x in srcmrp_unbuild: 
            data.append(
                _value_disct(
                    product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, 
                    uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                    okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                    reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = x.product_qty, product_in = 0, product_out = 0, return_qty = 0)
            )
        # =============================return ke whs==================================================
        src_return_whs = obj_move_line.search([
            ('state', '=', 'done'), domain_categ_id,('date','>', datetime_from),('date','<', datetime_to)
        ])
        for x in src_return_whs:
            if x.move_id.picking_id and x.move_id.picking_id.location_id.id == rtw_loc_id and x.move_id.picking_id.location_dest_id.id == rtw_dest_id:
                data.append( 
                    _value_disct(
                        product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, 
                        uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                        reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty=x.qty_done)
                )
        # =============================Gain/ Loss==================================================
        src_gain_lost = obj_move_line.search([
                ('state', '=', 'done'), ('product_id.categ_id','=',categ_id),('date','>=', datetime_from),('date','<=', datetime_to),('move_id.inventory_id','!=',False)
            ])
        for x in src_gain_lost:
            product_in = product_out = 0
            if x.location_dest_id.id == gain_dest_id:
                product_in = x.qty_done
            if x.location_dest_id.id == gain_loc_id:
                product_out = x.qty_done 
            data.append(
                _value_disct(
                    product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, 
                    uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                    okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                    reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = product_in, product_out = product_out, return_qty = 0)
            )
        return data

    def _get_data_sql(self, pm_config, date_start, date_end):
        list_okp = []
        list_out_okp = []
        categ_id = self._get_params(categ_xml_id)
        rtw_loc_id = self._get_params(rtw_loc_xml_id)
        rtw_dest_id = self._get_params(rtw_dest_xml_id)

        gain_loc_id = self._get_params(gain_loc_xml_id)
        gain_dest_id = self._get_params(gain_dest_xml_id)

        date_pm_config = pm_config.date

        date_from = date_start.date()
        date_to = date_end.date()

        datetime_from = date_start - relativedelta(hours=7)
        datetime_to = datetime_from + relativedelta(days=1)

        obj_move_line  = self.env['stock.move.line']
        obj_labeling = self.env['kmi.labeling']
        obj_unscramble = self.env['kmi.unscramble']
        obj_filling = self.env['kmi.filling']
        obj_banded = self.env['banded.usage']
        obj_packing = self.env['kmi.packing']
        obj_batch_mrp = self.env['batch.mrp.production']
        obj_mrp_unbuild = self.env['mrp.unbuild']
        obj_stock_inventory = self.env['stock.inventory']

        data = []
        domain_categ_id = ('product_id.categ_id','=',categ_id)
        if date_pm_config == date_from:
            print()
        else:
            # =============================OKP IN==================================================
            src_in_okp = obj_move_line.search([
                ('state', '=', 'done'), domain_categ_id,('date','>=', datetime_from),('date','<=', datetime_to)
            ])
            for x in src_in_okp:
                if x.move_id.picking_id.batch_production_id:
                    okp = False if not x.move_id.picking_id.batch_production_id else x.move_id.picking_id.batch_production_id.id
                    okp_in = okp_out = 0
                    if x.location_dest_id.id == rtw_loc_id:
                        okp_in = x.qty_done
                    if x.location_id.id == rtw_loc_id:
                        okp_out = x.qty_done
                    data.append( 
                        _value_disct(
                            product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, 
                            uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                            okp = okp, okp_in = okp_in, okp_out = okp_out, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                            reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                    )
            # =============================LABELING==================================================
            src_labeling = obj_labeling.search([('state','not in', ('cancel','model','draft_model')), ('product_labeling_id.categ_id','=',categ_id), ('date','>=', date_from),('date','<=', date_to)])
            for x in src_labeling:
                for i in self.env['kmi.labeling.material.usage'].search([('labeling_id','=',x.id)]):
                    data.append(
                        _value_disct(
                            product_id = x.product_labeling_id.id, produk_uom_id = x.product_labeling_id.uom_id.id, 
                            uom_id = x.product_labeling_id.uom_id.id, lot_id = i.lot_id.name, qty_awal = 0,
                            okp = False, okp_in = 0, okp_out = 0, shift = x.shift, fs_manual = i.fs_manual, bottle_out = 0, out_qty = 0, 
                            reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                    )
            # =============================Unscramble==================================================
            src_unscramble = obj_unscramble.search([('state','not in', ('cancel','model','draft_model')), ('product_silo_id.categ_id','=',categ_id), ('date','=', date_from)])
            for x in src_unscramble:
                for i in self.env['kmi.unscramble.bottle.line'].search([('unscramble_id','=',x.id)]):
                    data.append(
                        _value_disct(
                            product_id = x.product_silo_id.id, produk_uom_id = x.product_silo_id.uom_id.id, 
                            uom_id = x.product_silo_id.uom_id.id, lot_id = i.lot_id.name, qty_awal = 0,
                            okp = False, okp_in = 0, okp_out = 0, shift = x.shift, fs_manual = 0, bottle_out = i.bottle_out, out_qty = 0, 
                            reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                    )
            # =============================Filling Machine==================================================
            src_filling = obj_filling.search([('state','not in', ('cancel','model','draft_model')),('product_filling_id.categ_id','=',categ_id), ('date','=', date_from)])
            for x in src_filling:
                for i in self.env['kmi.filling.material.usage'].search([('filling_daily_report_id','=',x.id)]):
                    data.append(
                        _value_disct(
                            product_id = x.product_filling_id.id, produk_uom_id = x.product_filling_id.uom_id.id, 
                            uom_id = x.product_filling_id.uom_id.id, lot_id = i.lot_id.name, qty_awal = 0,
                            okp = False, okp_in = 0, okp_out = 0, shift = x.shift, fs_manual = 0, bottle_out = 0, out_qty = i.out_qty, reject = i.reject, 
                            total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                    )
            # =============================Stock Card Banded==================================================
            src_banded_usage = self.env['banded.usage'].search([('state','=', 'done'), ('date','=', date_from)])
            for banded in src_banded_usage:
                for x in banded.material_usage_line_1.filtered(lambda l: l.item_id.categ_id.id == categ_id):
                    data.append(
                        _value_disct(
                            product_id = x.item_id.id, produk_uom_id = x.item_id.uom_id.id, 
                            uom_id = x.item_id.uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                            okp = False, okp_in = 0, okp_out = 0, shift = x.banded_usage_id.shift, fs_manual = 0, bottle_out = 0, out_qty = 0, reject = 0, 
                            total_out = x.out, reject_out = x.reject, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                    )
                for x in banded.material_usage_line_2.filtered(lambda l: l.item_id.categ_id.id == categ_id):
                    data.append(
                        _value_disct(
                            product_id = x.item_id.id, produk_uom_id = x.item_id.uom_id.id, 
                            uom_id = x.item_id.uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                            okp = False, okp_in = 0, okp_out = 0, shift = x.banded_usage_id.shift, fs_manual = 0, bottle_out = 0, out_qty = 0, reject = 0, 
                            total_out = x.out, reject_out = x.reject, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                    )
            # =============================Packing==================================================
            src_packing = obj_packing.search([('state','not in', ('cancel','model','draft_model')), ('product_packing_id.categ_id','=',categ_id), ('date','=', date_from)])
            for x in src_packing:
                for i in self.env['kmi.packing.material.usage'].search([('packing_id','=',x.id)]):
                    qty = i.out_qty + i.sample_qc + i.reject_machine_qty + i.reject_coding_qty + i.reject_supplier_qty
                    data.append(
                        _value_disct(
                            product_id = x.product_packing_id.id, produk_uom_id = x.product_packing_id.uom_id.id, 
                            uom_id = x.product_packing_id.uom_id.id, lot_id = i.lot_id.name, qty_awal = 0,
                            okp = False, okp_in = 0, okp_out = 0, shift = x.shift, fs_manual = 0, bottle_out = 0, out_qty = 0, reject =0, 
                            total_out = 0, reject_out = 0, qty = qty, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                    )
            # =============================OKP OUT==================================================
            okp_src = self.env['batch.mrp.production'].search([('actual_closing','>=', datetime_from),('actual_closing','<=', datetime_to)])
            for okp in okp_src:
                for mo in okp.mrp_line:
                    for move in mo.move_raw_ids:
                        for x in move.move_line_ids:
                            number_bo = okp.number_bo
                            qty_done = x.qty_done
                            data.append(
                                _value_disct(
                                    product_id = move.product_id.id, produk_uom_id = move.product_id.uom_id.id, 
                                    uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                                    okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                                    reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = number_bo, qty_done = qty_done, product_qty = 0, product_in = 0, product_out = 0, return_qty = 0)
                            )
            # =============================Reject==================================================
            srcmrp_unbuild = obj_mrp_unbuild.search([('state', '=', 'done'), domain_categ_id, ('create_date','>=', datetime_from), ('create_date','<=', datetime_to)])
            for x in srcmrp_unbuild: 
                data.append(
                    _value_disct(
                        product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, 
                        uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                        reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = x.product_qty, product_in = 0, product_out = 0, return_qty = 0)
                )
            # =============================return ke whs==================================================
            src_return_whs = obj_move_line.search([
                ('state', '=', 'done'), domain_categ_id,('date','>=', datetime_from),('date','<=', datetime_to)
            ])
            for x in src_return_whs:
                if x.move_id.picking_id and x.move_id.picking_id.location_id.id == rtw_loc_id and x.move_id.picking_id.location_dest_id.id == rtw_dest_id:
                    data.append( 
                        _value_disct(
                            product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, 
                            uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                            okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                            reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = 0, product_out = 0, return_qty=x.qty_done)
                    )
            # =============================Gain/ Loss==================================================
            src_gain_lost = obj_move_line.search([
                ('state', '=', 'done'), ('product_id.categ_id','=',categ_id),('date','>=', datetime_from),('date','<=', datetime_to),('move_id.inventory_id','!=',False)
            ])
            for x in src_gain_lost:
                product_in = product_out = 0
                if x.location_dest_id.id == gain_dest_id:
                    product_in = x.qty_done
                if x.location_dest_id.id == gain_loc_id:
                    product_out = x.qty_done
                data.append(
                    _value_disct(
                        product_id = x.product_id.id, produk_uom_id = x.product_id.uom_id.id, 
                        uom_id = x.product_uom_id.id, lot_id = x.lot_id.name, qty_awal = 0,
                        okp = False, okp_in = 0, okp_out = 0, shift = 'Kosong', fs_manual = 0, bottle_out = 0, out_qty = 0, 
                        reject = 0, total_out = 0, reject_out = 0, qty = 0, number_bo = 'Kosong', qty_done = 0, product_qty = 0, product_in = product_in, product_out = product_out, return_qty = 0)
                )
            for x in data:
                okp_list_src = self.env['batch.mrp.production'].browse(x['okp'])
                if okp_list_src:
                    okp_name = okp_list_src.okp_id.name
                    if okp_name not in list_okp:
                        list_okp.append(okp_name)
                if x['number_bo'] not in list_out_okp and x['number_bo'] != 'Kosong':
                    list_out_okp.append(x['number_bo'])
        return data, list_okp, list_out_okp

    def action_export_xls(self):
        book = xlwt.Workbook()
        style_no_bold = xlwt.easyxf('borders: left thin, right thin, top thin, bottom thin;'
            'align: vert centre, horz left; font: name Helvetica Neue;')
        style_no_bold.num_format_str = '#,##0.00'
        style_header = xlwt.easyxf('font: colour white, bold 1, name Helvetica Neue; borders: left thin, right thin, top thin,'
            'bottom thin; align: vert centre, horz center; pattern: pattern solid, fore_colour dark_teal;')
        style_judul = xlwt.easyxf('font: colour black, bold 1, height 280, name Helvetica Neue; align: vert center, horz left;')
        style_judul_2 = xlwt.easyxf('font: colour black, bold 1, height 180, name Helvetica Neue; align: vert center, horz left;')
        
        header = ['No','PM Code','PM Name','Uom','No lot','Qty awal']
        dict_shidt = {
            'I' : 'Shift 1',
            'II': 'Shift 2',
            'III': 'Shift 3'}
        header_shift = ['I','II','III']

        pm_conf_src = self.env['mrp.pm.daily'].search([('state','=','done'),('date','<=',self.date_from)], limit=1)
        if not pm_conf_src:
            raise UserError(_('Tanggal mulai tidak boleh kurang dari tanggal opbal')) 

        date_list = []
        for dates in pd.date_range(self.date_from, self.date_to, freq='d'):
            date_list.append(dates)

        for days in date_list:
            name_sheet = days.strftime("%d %B")
            sheet = book.add_sheet(f'{name_sheet}', cell_overwrite_ok=True)
            sheet.normal_magn = 100

            col_width = 256 * 18
            try:
                for i in itertools.count():
                    sheet.col(i).width = col_width
                    sheet.col(0).width = 256 * 10
                    sheet.col(2).width = 256 * 40
                    sheet.col(3).width = 256 * 13
            except ValueError:
                pass
            
            colh = -1
            for x in header:
                colh += 1
                sheet.write_merge(0, 1, colh, colh, x, style_header)

            data_sql_dict = {}
            # =============================STOCK AWAL==================================================
            results_awal = self._get_stock_awal(pm_conf_src, days)
            data_sql_dict['awal'] = results_awal
            # =============================Data Days==================================================
            results_data, list_okp, list_out_okp = self._get_data_sql(pm_conf_src, days, days)
            data_sql_dict['Data'] = results_data
            
            data_dict = self._get_data_dict(data_sql_dict, list_okp, header_shift, list_out_okp)
            no = 1
            number = 0
            categ_id = self._get_params(categ_xml_id)
            for k, v in data_dict.items():
                produk = self.env['product.product'].browse(k)
                if produk.categ_id.id == categ_id:
                    for i in v:
                        v[i] = dict(sorted(v[i].items(), key=lambda x: x[0]))
                    for u, d in v.items():
                        no += 1
                        number += 1
                        qty_awal = sum(d['lot'])
                        sheet.write(no, 0, str(number), style_no_bold)
                        sheet.write(no, 1, produk.default_code, style_no_bold)
                        sheet.write(no, 2, produk.name, style_no_bold)
                        sheet.write(no, 3, produk.uom_id.name, style_no_bold)
                        sheet.write(no, 4, str(u), style_no_bold)
                        sheet.write(no, 5, qty_awal, style_no_bold)
                        no_okp = -1
                        colh_okp = 5
                        qty_okp = 0
                        qty_shift = 0
                        if d['okp']:
                            for p, n in dict(sorted(d['okp'].items())).items():
                                no_okp += 1
                                colh_okp += 1
                                sheet.write_merge(1, 1, colh_okp, colh_okp, p, style_header)
                                sheet.write(no, colh_okp, sum(n), style_no_bold)
                                qty_okp += sum(n)
                            awal_okp = colh_okp - no_okp
                            sheet.write_merge(0, 0, awal_okp, colh_okp, 'In Per OKP', style_header)
                        else:
                            colh_okp += 1
                            sheet.write_merge(1, 1, colh_okp, colh_okp, ' ', style_header)
                            sheet.write_merge(0, 0, colh_okp, colh_okp, 'In Per OKP', style_header)
                            sheet.write(no, colh_okp, 0, style_no_bold)
                        for s, h in dict(sorted(d['shift'].items())).items():
                            colh_okp += 1
                            sheet.write_merge(1, 1, colh_okp, colh_okp, s, style_header)
                            sheet.write(no, colh_okp, sum(h), style_no_bold)
                            qty_shift += sum(h)
                        sheet.write_merge(0, 0, colh_okp - 2, colh_okp, 'Out Per Shift', style_header)

                        no_out_okp = -1
                        colh_out_okp = colh_okp
                        qty_out_okp = 0
                        for l, m in dict(sorted(d['out_bo'].items())).items():
                            no_out_okp += 1
                            colh_out_okp += 1
                            sheet.write_merge(1, 1, colh_out_okp, colh_out_okp, l, style_header)
                            sheet.write(no, colh_out_okp, sum(m), style_no_bold)
                            qty_out_okp += sum(m)
                        awal_out_okp = colh_out_okp - no_out_okp
                        if awal_out_okp > colh_out_okp:
                            sheet.write_merge(1, 1, awal_out_okp, awal_out_okp, ' ', style_header)
                            sheet.write_merge(0, 0, awal_out_okp, awal_out_okp, 'Out Per BO', style_header)
                            sheet.write(no, awal_out_okp, 0, style_no_bold)
                            colh_okp += 1
                        else:
                            sheet.write_merge(0, 0, awal_out_okp, colh_out_okp, 'Out Per BO', style_header)
                        
                        col_akhir_nilai = max(awal_out_okp, colh_out_okp)

                        reject = sum(d['reject'])
                        returns = sum(d['return'])
                        total_gain_or_loss = sum(d['gain_or_loss'])
                        total_gain_or_loss = abs(total_gain_or_loss) if total_gain_or_loss < 0 else -total_gain_or_loss

                        nilai_positif = qty_awal + qty_okp
                        nilai_negatig = abs(qty_out_okp) + abs(reject) + abs(returns) + total_gain_or_loss
                        sisa = nilai_positif - nilai_negatig
                        fisik = 0
                        selisih = sisa - fisik

                        sheet.write_merge(0, 1, col_akhir_nilai + 1, col_akhir_nilai + 1, 'Reject', style_header)
                        sheet.write_merge(no, no, col_akhir_nilai + 1, col_akhir_nilai + 1, reject, style_no_bold)

                        sheet.write_merge(0, 1, col_akhir_nilai + 2, col_akhir_nilai + 2, 'return ke whs', style_header)
                        sheet.write_merge(no, no, col_akhir_nilai + 2, col_akhir_nilai + 2, returns, style_no_bold)

                        sheet.write_merge(0, 1, col_akhir_nilai + 3, col_akhir_nilai + 3, 'Gain/ Loss', style_header)
                        sheet.write_merge(no, no, col_akhir_nilai + 3, col_akhir_nilai + 3, total_gain_or_loss, style_no_bold)

                        sheet.write_merge(0, 1, col_akhir_nilai + 4, col_akhir_nilai + 4, 'Sisa', style_header)
                        sheet.write_merge(no, no, col_akhir_nilai + 4, col_akhir_nilai + 4, sisa, style_no_bold)

                        sheet.write_merge(0, 1, col_akhir_nilai + 5, col_akhir_nilai + 5, 'Aktual Fisik', style_header)
                        sheet.write_merge(no, no, col_akhir_nilai + 5, col_akhir_nilai + 5, fisik, style_no_bold)

                        sheet.write_merge(0, 1, col_akhir_nilai + 6, col_akhir_nilai + 6, 'selisih', style_header)
                        sheet.write_merge(no, no, col_akhir_nilai + 6, col_akhir_nilai + 6, selisih, style_no_bold)

        file_data = io.BytesIO()
        book.save(file_data)
        
        out = base64.encodebytes(file_data.getvalue())
        filename = 'PM Harian Periode :' + str(self.date_from.strftime('%d')) + \
            ' - ' + str(self.date_to.strftime('%d %B %Y')) + '.xls'
        self.write({'data_file': out, 'name': filename})

        model = self._name
        field_file = 'data_file'
        content = 'web/content/?model=%s&field=%s' % (model, field_file)
        download = '&download=true&id=%s&filename=%s' % (self.id, filename)
        url = content + download

        return {'type': 'ir.actions.act_url', 'url': url,}