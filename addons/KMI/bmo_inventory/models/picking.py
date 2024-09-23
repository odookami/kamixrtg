# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    ekspedisi = fields.Char('Ekspedisi')
    car_number = fields.Char('Vehicle')
    state = fields.Selection(selection_add=[('approved', 'Submited'),('ongoing','Ongoing'),('assigned',)])
    add_approved = fields.Boolean('Add Aprovel', default=False, compute="_compute_add_approved")
    lot_number_line = fields.One2many('stock.production.lot','picking_id',string='Lot Number',)
    group_product_ids = fields.Many2many("product.group.line", string="product Group")
    check_bhp = fields.Boolean(compute='_compute_check_bhp', string='BHP OK', store=True)
    delivery_return = fields.Boolean(string='Delivery Return',)
    is_open_popup = fields.Boolean('Is Pop UP', strore=False)
    already_state = fields.Boolean('Sudah pernah di State Ready')
    picking_return_id = fields.Many2one('stock.picking', string="Picking Return Id")
    # Used to search on pickings
    lot_id = fields.Many2one('stock.production.lot', 'Lot/Serial Number', related='move_line_nosuggest_ids.lot_id', readonly=True)
    #Archieve
    active = fields.Boolean('Active', default=True)
    
    @api.depends('state')
    def _compute_check_bhp(self):
        for o in self:
            if o.origin:
                if 'BHP' in o.origin and o.state in ('waiting','confirmed') and o.show_check_availability == True:
                    o.check_bhp = True
                else:
                    o.check_bhp = False
            else:
                o.check_bhp = False

    def check_group_product(self):
        self.ensure_one()
        data = []
        # for move in self.move_line_ids_without_package.filtered(lambda x : x.product_id):
        for move in self.move_ids_without_package.filtered(lambda x : x.product_id):
            group_product = self.env['product.group'].search([('product_id','=',move.product_id.id)])
            if group_product:
                for x in group_product:
                    for i in x.product_group_line:
                        data.append(i.id)
        self.group_product_ids = data

    def action_ongoing_kmi(self):
        for o in self:
            o.write({'state': 'ongoing'})

    def do_unreserve(self):
        for picking in self:
            move_line_ids = picking.mapped('move_line_ids_without_package').write({'qty_done' : 0})
            picking.group_product_ids = False
        return super(StockPicking, self).do_unreserve()
    
    @api.depends('state')
    def _compute_add_approved(self):
        for rec in self:
            location = rec.location_id.department_id.id
            location_dest = rec.location_dest_id.department_id.id
            if rec.picking_type_id.code == 'internal' and location != location_dest and rec.state == 'assigned':
                rec.write({
                    'add_approved'  : True,
                    'state'         : 'approved',
                })
            else:
                rec.add_approved = False
    
    def action_assign(self):
        res =  super(StockPicking, self).action_assign()
        self.check_group_product()
        self._compute_check_bhp()
        if not self.add_approved:
            self._compute_add_approved()

        if self.picking_type_code != 'incoming':
            for move_line in self.move_line_ids_without_package:
                move_line.qty_done = move_line.product_uom_qty
        
        if self.already_state == True:
            self.write({
                'state': 'assigned'
            })

        return res

    def action_back_to_draft(self):
        moves = self.mapped("move_lines")
        moves.action_back_to_draft()
    
    def action_add_approved(self):
        for rec in self:
            rec.already_state = False

            # chil = {
            #     'melting_amf': rec.melting_amf,
            #     'date_melting': rec.date_melting,
            #     'start_melting': rec.start_melting,
            #     'date_melting_amf': rec.date_melting_amf,
            #     'hour_melting_amf': rec.hour_melting_amf,
            #     # 'suhu': rec.suhu,
            #     'pressure': rec.pressure,
            #     'suhu_satu_jam': rec.suhu_satu_jam,
            #     'suhu_satu_jam_set': rec.suhu_satu_jam_set,
            #     'pressure_satu_jam': rec.pressure_satu_jam,
            #     'pressure_satu_jam_set': rec.pressure_satu_jam_set,
            #     'finish_melting': rec.finish_melting,
            #     'date_melting_pressure': rec.date_melting_pressure,
            #     'hour_melting_pressure': rec.hour_melting_pressure,
            #     'suhu_pressure': rec.suhu_pressure,
            #     'preparasi_amf': rec.preparasi_amf,
            #     'warna_amf': rec.warna_amf,
            #     'suhu_standar': rec.suhu_standar,
            # }
            # chil_2 = {
            #     'melting_amf_2':  rec.melting_amf_2,
            #     'date_melting_2':  rec.date_melting_2,
            #     'start_melting_2':  rec.start_melting_2,
            #     'date_melting_amf_2':  rec.date_melting_amf_2,
            #     'hour_melting_amf_2':  rec.hour_melting_amf_2,
            #     # 'suhu_2':  rec.suhu_2,
            #     'pressure_2':  rec.pressure_2,
            #     'suhu_satu_jam_2':  rec.suhu_satu_jam_2,
            #     'suhu_satu_jam_set_2':  rec.suhu_satu_jam_set_2,
            #     'pressure_satu_jam_2':  rec.pressure_satu_jam_2,
            #     'pressure_satu_jam_set_2':  rec.pressure_satu_jam_set_2,
            #     'finish_melting_2':  rec.finish_melting_2,
            #     'date_melting_pressure_2':  rec.date_melting_pressure_2,
            #     'hour_melting_pressure_2':  rec.hour_melting_pressure_2,
            #     'suhu_pressure_2':  rec.suhu_pressure_2,
            #     'preparasi_amf_2':  rec.preparasi_amf_2,
            #     'warna_amf_2':  rec.warna_amf_2,
            #     'suhu_standar_2':  rec.suhu_standar_2,
            # }
            # bene = {
            #     'date_start_thawing': rec.date_start_thawing,
            #     'hour_start_thawing': rec.hour_start_thawing,
            #     'date_finish_thawing': rec.date_finish_thawing,
            #     'hour_finish_thawing': rec.hour_finish_thawing,
            #     'y_n_melting': rec.y_n_melting,
            #     'date_melting_pernah': rec.date_melting_pernah,
            #     'age_melting_pernah': rec.age_melting_pernah,
            #     'date_start_meling': rec.date_start_meling,
            #     'hour_start_meling': rec.hour_start_meling,
            #     'no_kompor_meling': rec.no_kompor_meling,
            #     'no_jaket_meling': rec.no_jaket_meling,
            #     'date_finish_meling': rec.date_finish_meling,
            #     'hour_finish_meling': rec.hour_finish_meling,
            #     'suhu_jaket': rec.suhu_jaket,
            #     'check_pertama_jam': rec.check_pertama_jam,
            #     'suhu_pertama_jam': rec.suhu_pertama_jam,
            #     'check_kedua_jam': rec.check_kedua_jam,
            #     'suhu_kedua_jam': rec.suhu_kedua_jam,
            #     'suhu_after_melting': rec.suhu_after_melting,
            #     'warna_pse': rec.warna_pse,
            #     'abnormal': rec.abnormal,
            #     'jam_ke_1': rec.jam_ke_1,
            #     'suhu_ke_1': rec.suhu_ke_1,
            #     'warna_ke_1': rec.warna_ke_1,
            #     'jam_ke_2': rec.jam_ke_2,
            #     'suhu_ke_2': rec.suhu_ke_2,
            #     'warna_ke_2': rec.warna_ke_2,
            #     'jam_ke_3': rec.jam_ke_3,
            #     'suhu_ke_3': rec.suhu_ke_3,
            #     'warna_ke_3': rec.warna_ke_3,
            #     'jam_ke_4': rec.jam_ke_4,
            #     'suhu_ke_4': rec.suhu_ke_4,
            #     'warna_ke_4': rec.warna_ke_4,
            #     'tanggal_terima': rec.tanggal_terima,
            #     'jam_terima': rec.jam_terima,
            # }
            # bene_2 = {
            #     'date_start_thawing_2': rec.date_start_thawing_2,
            #     'hour_start_thawing_2': rec.hour_start_thawing_2,
            #     'date_finish_thawing_2': rec.date_finish_thawing_2,
            #     'hour_finish_thawing_2': rec.hour_finish_thawing_2,
            #     'y_n_melting_2': rec.y_n_melting_2,
            #     'date_melting_pernah_2': rec.date_melting_pernah_2,
            #     'age_melting_pernah_2': rec.age_melting_pernah_2,
            #     'date_start_meling_2': rec.date_start_meling_2,
            #     'hour_start_meling_2': rec.hour_start_meling_2,
            #     'no_kompor_meling_2': rec.no_kompor_meling_2,
            #     'no_jaket_meling_2': rec.no_jaket_meling_2,
            #     'date_finish_meling_2': rec.date_finish_meling_2,
            #     'hour_finish_meling_2': rec.hour_finish_meling_2,
            #     'suhu_jaket_2': rec.suhu_jaket_2,
            #     'check_pertama_jam_2': rec.check_pertama_jam_2,
            #     'suhu_pertama_jam_2': rec.suhu_pertama_jam_2,
            #     'check_kedua_jam_2': rec.check_kedua_jam_2,
            #     'suhu_kedua_jam_2': rec.suhu_kedua_jam_2,
            #     'suhu_after_melting_2': rec.suhu_after_melting_2,
            #     'warna_pse_2': rec.warna_pse_2,
            #     'abnormal_2': rec.abnormal_2,
            #     'jam_ke_1_2': rec.jam_ke_1_2,
            #     'suhu_ke_1_2': rec.suhu_ke_1_2,
            #     'warna_ke_1_2': rec.warna_ke_1_2,
            #     'jam_ke_2_2': rec.jam_ke_2_2,
            #     'suhu_ke_2_2': rec.suhu_ke_2_2,
            #     'warna_ke_2_2': rec.warna_ke_2_2,
            #     'jam_ke_3_2': rec.jam_ke_3_2,
            #     'suhu_ke_3_2': rec.suhu_ke_3_2,
            #     'warna_ke_3_2': rec.warna_ke_3_2,
            #     'jam_ke_4_2': rec.jam_ke_4_2,
            #     'suhu_ke_4_2': rec.suhu_ke_4_2,
            #     'warna_ke_4_2': rec.warna_ke_4_2,
            #     'tanggal_terima_2': rec.tanggal_terima_2,
            #     'jam_terima_2': rec.jam_terima_2,
            # }
            # if rec.lot_amf_1_id and rec.check_tipe_product == 'Chilgo':
            #     print(chil)
            #     for x, y in chil.items():
            #         if y==0:
            #             raise ValidationError(_('Analisa AMF Lot 1 ada yang kosong'))

            # if rec.lot_amf_1_id and rec.check_tipe_product == 'Benecol':
            #     print(bene)
            #     for x, y in bene.items():
            #         if y==0:
            #             raise ValidationError(_('Analisa AMF Lot 1 ada yang kosong'))
            
            # if rec.lot_amf_2_id and rec.check_tipe_product == 'Chilgo':
            #     for x, y in chil_2.items():
            #         if y==0:
            #             raise ValidationError(_('Analisa AMF Lot 2 ada yang kosong'))

            # if rec.lot_amf_2_id and rec.check_tipe_product == 'Benecol':
            #     for x, y in bene_2.items():
            #         if y==0:
            #             raise ValidationError(_('Analisa AMF Lot 2 ada yang kosong'))

            location = rec.location_id.department_id
            location_dest = rec.location_dest_id.department_id
            if rec.picking_type_id.code == 'internal' and location.id != location_dest.id and self.env.user.id not in location.user_ids.ids:
                raise ValidationError(_('User Yang Bisa Submit hanya User Tertentu Saja !!!!')) 
            rec.write({'state' : 'assigned', 'already_state': True})
            
    def update_quant_reservation(self):
        quants = self.env["stock.quant"].search([])
        move_line_ids = []
        warning = ""
        for quant in quants:
            move_lines = self.env["stock.move.line"].search(
                [
                    ("product_id", "=", quant.product_id.id),
                    ("location_id", "=", quant.location_id.id),
                    ("lot_id", "=", quant.lot_id.id),
                    ("package_id", "=", quant.package_id.id),
                    ("owner_id", "=", quant.owner_id.id),
                    ("product_qty", "!=", 0),
                    ("picking_id", "=",self.id)
                ]
            )
            move_line_ids += move_lines.ids
            reserved_on_move_lines = sum(move_lines.mapped("product_qty"))
            move_line_str = str.join(", ", [str(move_line_id) for move_line_id in move_lines.ids])
            if quant.location_id.should_bypass_reservation():
                if quant.reserved_quantity != 0:
                    quant.write({"reserved_quantity": 0})
            else:
                if quant.reserved_quantity == 0:
                    if move_lines:
                        move_lines.with_context(bypass_reservation_update=True).write({"product_uom_qty": 0})
                elif quant.reserved_quantity < 0:
                    quant.write({"reserved_quantity": 0})
                    if move_lines:
                        move_lines.with_context(bypass_reservation_update=True).write({"product_uom_qty": 0})
                else:
                    if reserved_on_move_lines != quant.reserved_quantity:
                        move_lines.with_context(bypass_reservation_update=True).write({"product_uom_qty": 0})
                        quant.write({"reserved_quantity": 0})
                    else:
                        if any(move_line.product_qty < 0 for move_line in move_lines):
                            move_lines.with_context(bypass_reservation_update=True).write({"product_uom_qty": 0})
                            quant.write({"reserved_quantity": 0})
        move_lines = self.env["stock.move.line"].search(
            [
                ("product_id.type", "=", "product"),
                ("product_qty", "!=", 0),
                ("id", "not in", move_line_ids),
            ]
        )
        move_lines_to_unreserve = []
        for move_line in move_lines:
            if not move_line.location_id.should_bypass_reservation():
                move_lines_to_unreserve.append(move_line.id)
        if len(move_lines_to_unreserve) > 1:
            self.env.cr.execute(
                """ UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id in %s ; """ % (tuple(move_lines_to_unreserve),)
            )
        elif len(move_lines_to_unreserve) == 1:
            self.env.cr.execute(
                """ UPDATE stock_move_line SET product_uom_qty = 0, product_qty = 0 WHERE id = %s ; """ % (move_lines_to_unreserve[0])
            )

    def button_validate(self):
        for rec in self:
            location = rec.location_id.department_id
            location_dest = rec.location_dest_id.department_id
            if rec.picking_type_id.code == 'internal' and location.id != location_dest.id and self.env.user.id not in location_dest.user_ids.ids:
                raise ValidationError(_('User Yang Bisa Validate hanya User Tertentu Saja !!!!')) 
            if rec.picking_type_id.code == 'outgoing':
                for line in rec.move_ids_without_package:
                    if line.product_uom_qty_origin > 0 and line.quantity_done > line.product_uom_qty_origin: 
                        raise ValidationError(_("DO, Qty Done Tidak Boleh Melebihi Demand"))
                    if line.product_uom_qty_origin == 0 and line.quantity_done > line.product_uom_qty:
                        raise ValidationError(_("DO, Qty Done Tidak Boleh Melebihi Demand"))
            return super(StockPicking, self).button_validate()
    
    # Auto isi line ketika dest loc scrap
    # @api.onchange('location_id','location_dest_id')
    # def _onchange_scrap_location(self):
    #     for rec in self:
    #         lines_dict = {}
    #         line_value = []
    #         if rec.location_dest_id.scrap_location:
    #             sl_obj = self.env['stock.quant'].search([('location_id', '=', rec.location_id.id)])
    #             for sl in sl_obj:
    #                 if sl.product_id.id not in lines_dict:
    #                     lines_dict[sl.product_id.id] = [sl.quantity]
    #                 else:
    #                 	lines_dict[sl.product_id.id].append(sl.quantity)
    #             for k, v in lines_dict.items():
    #                 product = self.env['product.product'].browse(k)
    #                 qty = sum(v)
    #                 line_value.append((0,0,{
    #                     'product_id'                : product.id,
    #                     'name'                      : product.name,
    #                     'product_uom_qty'           : qty,
    #                     'product_uom'               : product.uom_id.id,
    #                     'location_id'               : rec.location_id.id,
    #                     'location_dest_id'          : rec.location_dest_id.id,
    #                     # 'picking_type_id'           : rec.picking_id.picking_type_id,
    #                 }))
    #         rec.move_ids_without_package = False
    #         value = {'move_ids_without_package': line_value} if line_value else {}
    #         return {'value': value}

    @api.model
    def create(self, vals):
        vals['immediate_transfer'] = False
        res = super(StockPicking, self).create(vals)
        res.immediate_transfer = False
        res.do_unreserve()
        return res