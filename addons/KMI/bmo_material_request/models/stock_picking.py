# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.bmo_mrp.models.product import state_tipe
from odoo.exceptions import Warning, UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round

class BatchMrpProduction(models.Model):
    _inherit = 'batch.mrp.production'

    cek_move_qty = fields.Boolean("Cek", default=False)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    cek_move_qty = fields.Boolean("Cek", default=False)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition', string='Purchase Requisition', readonly=True)
    tipe = fields.Selection(
        state_tipe, string='Type OKP', tracking=True)
    batch_production_id = fields.Many2one(
        'batch.mrp.production', string='OKP')
    master_okp_id = fields.Many2one(
        "mrp.okp", "Master OKP", related='batch_production_id.okp_id', store=True)
    mo_id = fields.Many2one(
        "mrp.production", "MO")
    product_batch_id = fields.Many2one(
        "product.product", "Product", related="batch_production_id.product_id")
    batch_proses = fields.Float(
        string='Batch Proses', related="batch_production_id.batch_proses")
    uom_id = fields.Many2one(
        'uom.uom',
        string='Standar Formulasi',
        related="batch_production_id.bom_id.product_uom_id",
    )
    old_picking_id = fields.Many2one(
        "stock.picking", string="Old Picking")
    generate_okp =fields.Boolean(
        "Generate OKP", default=False)
    cek_product_amf = fields.Boolean(
        "Cek AMF", default=False, compute="_compute_cek_product_amf")    
    lot_amf_1_id = fields.Many2one(
        "stock.production.lot", string='AMF (lot ke-1)')
    lot_amf_2_id = fields.Many2one(
        "stock.production.lot", string='AMF (lot ke-2)')
    product_chilgo = fields.Boolean(
        "Cek chilgo", default=False, )
    product_benecol = fields.Boolean(
        "Cek benecol", default=False, ) 
    check_tipe_product = fields.Selection([
        ('Chilgo', 'Chilgo'), ('Benecol', 'Benecol'),], string='Tipe Batch product Chilgo / Benecol')
    
    @api.depends('move_line_ids_without_package', 'move_ids_without_package', 'state')
    def _compute_cek_product_amf(self):
        product_amf_ids = self.env['res.company']._company_default_get('material.settings').product_amf_ids
        product_product_ids = self.env['res.company']._company_default_get('material.settings').product_product_ids
        for rec in self:
            data_lot = []
            data_lot_2 = []
            for line in rec.move_line_ids_without_package.filtered(lambda x: x.product_id.id in product_amf_ids.ids):
                if len(data_lot) <= 2:
                    data_lot.append(line.lot_id.id)
            for line in rec.move_line_ids_without_package.filtered(lambda x: x.product_id.id in product_product_ids.ids):
                if len(data_lot_2) <= 2:
                    data_lot_2.append(line.lot_id.id)
            if data_lot:
                rec.cek_product_amf = True
                rec.check_tipe_product = "Chilgo"
                if len(data_lot) >= 2:
                    rec.lot_amf_1_id = data_lot[0]
                    rec.lot_amf_2_id = data_lot[1]
                else:
                    rec.lot_amf_1_id = data_lot[0]
            elif data_lot_2:
                rec.cek_product_amf = True
                rec.check_tipe_product = "Benecol"
                if len(data_lot_2) >= 2:
                    rec.lot_amf_1_id = data_lot_2[0]
                    rec.lot_amf_2_id = data_lot_2[1]
                else:
                    rec.lot_amf_1_id = data_lot_2[0]
            else:
                rec.cek_product_amf = False
    
    lot_no_amf = fields.Char("Lot No. AMF")
    lot_no_amf_2 = fields.Char("Lot No. AMF 2")
    # ------------------------------------------------chilgo------------------------------------------------
    # ---------------------------------------------------- Preparasi AMF
    melting_amf = fields.Char("AMF Melting")
    melting_amf_2 = fields.Char("AMF Melting 2")
    date_melting = fields.Char("Date Melting")
    date_melting_2 = fields.Char("Date Melting 2")
    start_melting = fields.Char("Start Melting")
    start_melting_2 = fields.Char("Start Melting 2")
    date_melting_amf = fields.Char("Date Meling AMF")
    date_melting_amf_2 = fields.Char("Date Meling AMF 2")
    hour_melting_amf = fields.Char("Hour Meling AMF")
    hour_melting_amf_2 = fields.Char("Hour Meling AMF 2")
    suhu = fields.Char("Suhu")
    suhu_2 = fields.Char("Suhu 2")
    pressure = fields.Char("Pressure")
    pressure_2 = fields.Char("Pressure 2")
    # ---------------------------------------------------- Presure
    suhu_satu_jam = fields.Char("Suhu (1 jam)")
    suhu_satu_jam_2 = fields.Char("Suhu (1 jam)	2")
    suhu_satu_jam_set = fields.Char("Suhu (1.5 jam)	")
    suhu_satu_jam_set_2 = fields.Char("Suhu (1.5 jam) 2")
    pressure_satu_jam = fields.Char("Pressure (1 jam)	")
    pressure_satu_jam_2 = fields.Char("Pressure (1 jam) 2")
    pressure_satu_jam_set = fields.Char("Pressure (1.5 jam)	")
    pressure_satu_jam_set_2 = fields.Char("Pressure (1.5 jam) 2")
    finish_melting = fields.Char("Finish Melting")
    finish_melting_2 = fields.Char("Finish Melting 2")
    date_melting_pressure = fields.Char("Date Meling pressure")
    date_melting_pressure_2 = fields.Char("Date Meling pressure 2")
    hour_melting_pressure = fields.Char("Hour Meling pressure")
    hour_melting_pressure_2 = fields.Char("Hour Meling pressure 2")
    suhu_pressure = fields.Char("Suhu Pressure")
    suhu_pressure_2 = fields.Char("Suhu Pressure 2")
    # ----------------------------------------------------
    preparasi_amf = fields.Char("Preparasi AMF")
    preparasi_amf_2 = fields.Char("Preparasi AMF 2")
    warna_amf = fields.Char("Warna AMF")
    warna_amf_2 = fields.Char("Warna AMF 2")
    suhu_standar = fields.Char("Suhu (standar : 60 - 95°C)")
    suhu_standar_2 = fields.Char("Suhu (standar : 60 - 95°C) 2")
    # ------------------------------------------------chilgo------------------------------------------------

    # ------------------------------------------------nutrive benecol------------------------------------------------
    date_start_thawing = fields.Char("Start Thawing (tanggal)")
    date_start_thawing_2 = fields.Char("Start Thawing (tanggal) 2")
    hour_start_thawing = fields.Char("Start Thawing (jam)")
    hour_start_thawing_2 = fields.Char("Start Thawing (jam) 2")
    date_finish_thawing = fields.Char("Finish Thawing (tanggal)")
    date_finish_thawing_2 = fields.Char("Finish Thawing (tanggal) 2")
    hour_finish_thawing = fields.Char("Finish Thawing (jam)")
    hour_finish_thawing_2 = fields.Char("Finish Thawing (jam) 2")

    y_n_melting = fields.Selection([('Y','Y'),('n','n')],'Y or N')
    y_n_melting_2 = fields.Selection([('Y','Y'),('n','n')],'Y or N')
    date_melting_pernah = fields.Char("Tanggal Melting")
    date_melting_pernah_2 = fields.Char("Tanggal Melting 2")
    age_melting_pernah = fields.Char("Umur Melting sebelumnya")
    age_melting_pernah_2 = fields.Char("Umur Melting sebelumnya 2")

    date_start_meling = fields.Char("Start Melting (tanggal)")
    date_start_meling_2 = fields.Char("Start Melting (tanggal) 2")
    hour_start_meling = fields.Char("Start Melting (jam)")
    hour_start_meling_2 = fields.Char("Start Melting (jam) 2")
    no_kompor_meling = fields.Char("Nomor Kompor")
    no_kompor_meling_2 = fields.Char("Nomor Kompor 2")
    no_jaket_meling = fields.Char("Nomor Jaket")
    no_jaket_meling_2 = fields.Char("Nomor Jaket 2")
    date_finish_meling = fields.Char("Finish Melting (tanggal)")
    date_finish_meling_2 = fields.Char("Finish Melting (tanggal) 2")
    hour_finish_meling = fields.Char("Finish Melting (jam)")
    hour_finish_meling_2 = fields.Char("Finish Melting (jam) 2")

    suhu_jaket = fields.Char("Suhu (standar : 60 - 95°C)")
    suhu_jaket_2 = fields.Char("Suhu (standar : 60 - 95°C) 2")
    check_pertama_jam = fields.Char("Check Pertama Jam")
    check_pertama_jam_2 = fields.Char("Check Pertama Jam 2")
    suhu_pertama_jam = fields.Char("Suhu Pertama")
    suhu_pertama_jam_2 = fields.Char("Suhu Pertama 2")
    check_kedua_jam = fields.Char("Check Kedua Jam")
    check_kedua_jam_2 = fields.Char("Check Kedua Jam 2")
    suhu_kedua_jam = fields.Char("Suhu Kedua")
    suhu_kedua_jam_2 = fields.Char("Suhu Kedua 2")
    suhu_after_melting = fields.Char("Suhu PSE (75-80°C After Melting 15 Jam)")
    suhu_after_melting_2 = fields.Char("Suhu PSE (75-80°C After Melting 15 Jam) 2")
    warna_pse = fields.Char("Warna PSE")
    warna_pse_2 = fields.Char("Warna PSE 2")
    abnormal = fields.Char("Abnormal")
    abnormal_2 = fields.Char("Abnormal 2")
    jam_ke_1 = fields.Char("Jam ke-1")
    jam_ke_1_2 = fields.Char("Jam ke-1 2")
    suhu_ke_1 = fields.Char("Suhu ke-1")
    suhu_ke_1_2 = fields.Char("Suhu ke-1 2")
    warna_ke_1 = fields.Char("Warna ke-1")
    warna_ke_1_2 = fields.Char("Warna ke-1 2")
    jam_ke_2 = fields.Char("Jam ke-2")
    jam_ke_2_2 = fields.Char("Jam ke-2 2")
    suhu_ke_2 = fields.Char("Suhu ke-2")
    suhu_ke_2_2 = fields.Char("Suhu ke-2 2")
    warna_ke_2 = fields.Char("Warna ke-2")
    warna_ke_2_2 = fields.Char("Warna ke-2 2")
    jam_ke_3 = fields.Char("Jam ke-3")
    jam_ke_3_2 = fields.Char("Jam ke-3 2")
    suhu_ke_3 = fields.Char("Suhu ke-3")
    suhu_ke_3_2 = fields.Char("Suhu ke-3 2")
    warna_ke_3 = fields.Char("Warna ke-3")
    warna_ke_3_2 = fields.Char("Warna ke-3 2")
    jam_ke_4 = fields.Char("Jam ke-4")
    jam_ke_4_2 = fields.Char("Jam ke-4 2")
    suhu_ke_4 = fields.Char("Suhu ke-4")
    suhu_ke_4_2 = fields.Char("Suhu ke-4 2")
    warna_ke_4 = fields.Char("Warna ke-4")
    warna_ke_4_2 = fields.Char("Warna ke-4 2")

    tanggal_terima = fields.Char("Tanggal Serah Terima")
    tanggal_terima_2 = fields.Char("Tanggal Serah Terima 2")
    jam_terima = fields.Char("Jam Serah Terima")
    jam_terima_2 = fields.Char("Jam Serah Terima 2")

    # ------------------------------------------------nutrive benecol------------------------------------------------


    def update_data(self):
        self._compute_cek_product_amf()

    def action_confirm(self):
        res = super(StockPicking, self).action_confirm()
        for rec in self:
            rec._compute_cek_product_amf()
            if rec.custom_requisition_id:
                if rec.custom_requisition_id.okp_id:
                    mr = rec.custom_requisition_id
                    okp_id = mr.mo_id
                    conf_default = self.env['master.default.location'].search([
                        ('config_id','=',mr.conf_special_product_id.id),('location_id','=',rec.location_id.id), ('dest_location_id','=',rec.location_dest_id.id)
                    ])
                    if conf_default.sequence_ref != 1:
                        picking = rec.search([('id','!=',rec.id),('custom_requisition_id','=',rec.custom_requisition_id.id)], limit=1)
                        if picking.state != 'done':
                            raise Warning(_(f'Mohon Selesaikan Dulu Proses Trasfer {picking.name}'))
                        okp_id.write({'cek_move_qty' : True})
                rec.do_unreserve()
                rec.write({'state' : 'confirmed'})
        return res
    
    def action_assign(self):
        if self.custom_requisition_id and self.tipe == 'Mixing' and self.old_picking_id:
            self.check_group_product()
            self.filtered(lambda picking: picking.state == 'draft').action_confirm()
            moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
            if not moves:
                raise UserError(_('Nothing to check the availability for.'))
            package_level_done = self.mapped('package_level_ids').filtered(lambda pl: pl.is_done and pl.state == 'confirmed')
            package_level_done.write({'is_done': False})
            moves._action_assign_new_kmi()
            package_level_done.write({'is_done': True})
            return True
        else:
            self._compute_cek_product_amf()
            return super(StockPicking, self).action_assign()

    def do_unreserve(self):
        if self.custom_requisition_id and self.tipe == 'Mixing' and self.old_picking_id:
            for line in self.move_ids_without_package:
                for ml in line.move_line_ids:
                    src_ml = self.env['stock.move.line'].search([('product_id', '=', ml.product_id.id),('location_dest_id','=',ml.location_id.id),('lot_id','=',ml.lot_id.id),('picking_id', '=', self.old_picking_id.id)])
                    for i in src_ml:
                        i.write({'qty_used_okp' : i.qty_used_okp - ml.product_uom_qty})
        res = super(StockPicking, self).do_unreserve()
        return res

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            # for line in rec.move_ids_without_package:
            #     if rec.tipe == 'Mixing':
            #         if line.product_uom_qty_origin > 0 and line.quantity_done > line.product_uom_qty_origin:
            #             raise ValidationError(_("OKP 'Mixing', Qty Done Tidak Boleh Melebihi Demand"))
            #         if line.product_uom_qty_origin == 0 and line.quantity_done > line.product_uom_qty:
            #             raise ValidationError(_("OKP 'Mixing', Qty Done Tidak Boleh Melebihi Demand"))

            if rec.picking_type_id.code == 'outgoing':
                for a in rec.move_line_ids_without_package:
                    if not a.verifikator_admin:
                        raise ValidationError(_('Verifikator Admin belum di isi'))

            rec._compute_cek_product_amf()
            if rec.custom_requisition_id:
                rec.custom_requisition_id.write({'state' : 'receive'})
                if rec.state in ('done') and rec.tipe == 'Mixing' and not rec.generate_okp:
                    data_conf = self.env['master.default.location'].search([('tipe','=','Mixing')], limit=1)
                    if not data_conf.dest_location_2_id or not data_conf.picking_type_2_id:
                        raise Warning(_("Mohon Lengkapi Config untuk Tipe Mixing"))
                    stock_obj = self.env['stock.picking']
                    move_obj = self.env['stock.move']
                    picking_type = self.env['stock.picking.type'].search([('code','=','internal'),('default_location_dest_id','=',rec.location_dest_id.id)])
                    for mrp in rec.batch_production_id.mrp_line:
                        stock_id = stock_obj.sudo().create({
                            'location_id'           : data_conf.dest_location_id.id,
                            'location_dest_id'      : data_conf.dest_location_2_id.id,
                            'picking_type_id'       : data_conf.picking_type_2_id.id,
                            'note'                  : rec.custom_requisition_id.reason,
                            'custom_requisition_id' : rec.custom_requisition_id.id,
                            'origin'                : rec.name + ' ' + rec.custom_requisition_id.name,
                            'company_id'            : rec.company_id.id,
                            'tipe'                  : rec.tipe,
                            'batch_production_id'   : rec.batch_production_id.id,
                            'old_picking_id'        : rec.id,
                            'mo_id'                 : mrp.id,
                            'immediate_transfer'    : False,
                            'generate_okp'          : True,
                        })
                        stock_id.write({'name' : str(stock_id.name) + ' - ' + str(mrp.number_ref)})
                        for line in mrp.move_raw_ids:
                            # if line.product_id.type == 'product':
                            move_obj.sudo().create({
                                'product_id'                : line.product_id.id,
                                'name'                      : line.product_id.name,
                                'product_uom_qty'           : line.product_uom_qty,
                                'product_uom'               : line.product_uom.id,
                                'location_id'               : stock_id.location_id.id,
                                'location_dest_id'          : stock_id.location_dest_id.id,
                                'picking_type_id'           : stock_id.picking_type_id.id,
                                'picking_id'                : stock_id.id,
                                'company_id'                : rec.company_id.id,
                                'mo_id'                     : stock_id.mo_id.id,
                            })
                else:
                    if rec.state == 'done' and rec.tipe == 'Mixing' and rec.generate_okp == True:
                        for move in rec.move_ids_without_package:
                            for m_line in move.move_line_ids:
                                if m_line.lot_id:
                                    m_line.lot_id.write({'mo_id' : move.mo_id.id})
                if 'INT' in rec.origin:
                    for detop in rec.move_line_ids_without_package:
                        if detop.verifikator_check == True and not detop.verifikator:
                            raise ValidationError(_('Verifikator belum di isi'))
        
        return res

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
    )
    
    verifikator = fields.Selection([('yes', 'Yes'), ('no', 'No'),], string='Verifikator (PRD)')
    mo_id = fields.Many2one("mrp.production", "MO")

    def _prepare_move_line_vals_manual_kmi(self, quantity=None, reserved_quant=None, quant=None):
        result = super(StockMove, self)._prepare_move_line_vals_manual_kmi(quantity, reserved_quant)
        if self.picking_id and self.picking_id.old_picking_id and self.product_id.type == 'product':
            src_ml = self.env['stock.move.line'].search([
                ('product_id', '=', result['product_id']),('location_dest_id','=',result['location_id']),
                ('lot_id','=',result['lot_id']),('picking_id', '=', self.picking_id.old_picking_id.id)])
            src_ml.sudo().write({"qty_used_okp" : src_ml.qty_used_okp + result['product_uom_qty']})
        return result
    
    def _action_assign_new_kmi(self):
        assigned_moves = self.env['stock.move']
        partially_available_moves = self.env['stock.move']
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
            rounding = roundings[move]
            missing_reserved_uom_quantity = move.product_uom_qty - reserved_availability[move]
            missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity, move.product_id.uom_id, rounding_method='HALF-UP')
            if move._should_bypass_reservation():
                if move.product_id.tracking == 'serial' and (move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                    for i in range(0, int(missing_reserved_quantity)):
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=1))
                else:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                            ml.location_id == move.location_id and
                                                            ml.location_dest_id == move.location_dest_id and
                                                            ml.picking_id == move.picking_id and
                                                            not ml.lot_id and
                                                            not ml.package_id and
                                                            not ml.owner_id)
                    if to_update:
                        to_update[0].product_uom_qty += missing_reserved_uom_quantity
                    else:
                        move_line_vals_list.append(move._prepare_move_line_vals_manual_kmi(quantity=missing_reserved_quantity))
                assigned_moves |= move
            else:
                if float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                    assigned_moves |= move
                elif not move.move_orig_ids:
                    if move.procure_method == 'make_to_order':
                        continue
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=rounding):
                        assigned_moves |= move
                        continue
                    forced_package_id = move.package_level_id.package_id or None
                    rounding = move.product_id.uom_id.rounding
                    product_uom_qty = move.product_uom_qty
                    src_ml = self.env['stock.move.line'].search([('product_id', '=', move.product_id.id),('picking_id', '=', move.picking_id.old_picking_id.id)])
                    for ml in src_ml:
                        need = ml.qty_done - ml.qty_used_okp 
                        if  ml.qty_used_okp >= ml.qty_done:
                            continue
                        available_quantity = move._get_available_quantity(ml.location_id, package_id=forced_package_id)
                        if available_quantity <= 0:
                            continue
                        if move.reserved_availability >= move.product_uom_qty:
                            continue
                        if move.product_uom.id != move.product_id.uom_id.id:
                            product_uom_qty = move.product_uom._compute_quantity(need, move.product_id.uom_id)
                        quant = self.env['stock.quant'].search([('product_id','=',move.product_id.id),('location_id','=',ml.location_dest_id.id),('lot_id','=',ml.lot_id.id)],limit=1)
                        taken_quantity = move._update_reserved_quantity_manual_kmi(product_uom_qty, need, ml.location_dest_id, lot_id=ml.lot_id, package_id=False, quant=quant, strict=False)
                        product_uom_qty -= taken_quantity
                        if float_is_zero(taken_quantity, precision_rounding=rounding):
                            continue
                        if float_compare(need, taken_quantity, precision_rounding=rounding) == 0:
                            assigned_moves |= move
                        else:
                            partially_available_moves |= move

        self.env['stock.move.line'].create(move_line_vals_list)
        partially_available_moves.write({'state': 'partially_available'})
        assigned_moves.write({'state': 'assigned'})
        self.mapped('picking_id')._check_entire_pack()

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    verifikator = fields.Selection([('yes', 'Yes'), ('no', 'No'),], string='Verifikator (PRD)')
    verifikator_admin = fields.Selection([('yes', 'Yes'), ('no', 'No'),], string='Verifikator Admin')
    mo_id = fields.Many2one("mrp.production", "MO")
    verifikator_check = fields.Boolean(
        "Cek Verifikator", default=False, compute="_compute_verifikator_check")
    qty_used_okp = fields.Float(
        "Qty Used", default=0.0, digits=(30,4), copy=False)
    # verifikator_check_admin = fields.Boolean(
    #     "Cek Verifikator Admin", default=False, compute="_compute_verifikator_admin")

    def _compute_verifikator_check(self):
        for rec in self:
            if rec.picking_id.custom_requisition_id:
                rec.verifikator_check = True
            else:
                rec.verifikator_check = False
