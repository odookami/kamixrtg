
# -*- coding: utf-8 -*-

from typing import Tuple
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round

class BatchMrpProduction(models.Model):
    _inherit = 'batch.mrp.production'

    bhp_goods_qty = fields.Float(string='Goods from BHP')
    
class MrpProductonPacking(models.Model):
    _inherit = 'mrp.production.packing'

    total_output = fields.Float(string='Total Output', tracking=True)
    mrp_packing_line = fields.One2many('mrp.production.packing.line', 
        inverse_name='mrp_packing_id', string='Detail BHP')

    # @api.constrains('okp_id')
    # def _check_okp(self):
    #     for record in self:
    #         batch_ids = record._get_batch_mrp(record.okp_id, record.packing_type)
    #         all_goods_qty = sum(x.goods_qty for x in batch_ids)
    #         if all_goods_qty <= 0:
    #             return
    #         for batch in batch_ids:
    #             qty_dict = {
    #                 batch.bhp_goods_qty >= batch.goods_qty: 
    #                 'Goods dari BHP sudah mencapai Goods pada OKP',
    #                 batch.bhp_goods_qty < batch.goods_qty and record.packing_type == 'Banded':
    #                 'Goods dari BHP Packing belum mencapai Goods pada OKP'
    #             }
    #             print(batch.goods_qty, "###B###", batch.bhp_goods_qty)
    #         # print(qty_dict, "###Q###")
    #         if True in qty_dict:
    #             raise ValidationError(qty_dict[True])
    
    def action_done(self):
        for record in self:
            vals = {'bhp_goods_qty': sum(x.total_output or \
                x.total_output_banded for x in record.mrp_packing_line)}
            batch_ids = record._get_batch_mrp(record.okp_id, record.packing_type)
            for batch in batch_ids:
                batch.write(vals)
        return self.write({'state': 'done'})

class MrpProductonPackingLine(models.Model):
    _name = 'mrp.production.packing.line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Detail BHP Pack / Banded'

    # @api.model
    # def default_get(self, fields):
    # 	res = super(MrpProductonPackingLine, self).default_get(fields)
    # 	print(res, "###R###")
    # 	return res

    name = fields.Char(string='Name', tracking=True)
    mrp_packing_id = fields.Many2one('mrp.production.packing', 
        string='No. BHP', ondelete='cascade')
    mrp_packing_state = fields.Selection(related='mrp_packing_id.state', string='BHP status')
    packing_type = fields.Selection(related='mrp_packing_id.packing_type')
    state = fields.Selection(string='Status', selection=[('in_progress', 'In Progress'), 
        ('hold', 'Hold'), ('reject', 'Rejected'), ('done', 'Done'), 
        ('revisi', 'Revisi')], default='in_progress', tracking=True)

    
    @api.model
    def create(self, values):
        # Add code here
        name = ''
        if 'mrp_packing_id' in values:
            mrp_packing_obj = self.env['mrp.production.packing']
            name = mrp_packing_obj.browse([values['mrp_packing_id']]).name
        values['name'] = 'Detail BHP - ' + name
        return super(MrpProductonPackingLine, self).create(values)

    # * pallet
    pallet_seq_no = fields.Char(string='No Urut Pallet ', tracking=True)
    package_id = fields.Many2one('stock.quant.package', 
        string='No Urut Pallet', tracking=True)
    
    _sql_constraints = [
            ('bhp_package_uniq', 'unique(package_id, mrp_packing_id)', 
                'No Urut Pallet sudah digunakan untuk BHP yang sama !'),
        ]

    @api.onchange('package_id')
    def _onchange_package_id(self):
        # value = {}
        domain = {}
        ctx = self._context
        print("###C###", self._context)
        if 'mrp_packing_id' in ctx:
            if ctx['mrp_packing_id']:
                mrp_packing_obj = self.env['mrp.production.packing']
                mrp_packing_line = mrp_packing_obj.browse(ctx['mrp_packing_id']).mrp_packing_line
                package_ids = [x.package_id.id for x in mrp_packing_line]
                domain = {'package_id': [('id', 'not in', package_ids)]}
        return {'domain': domain}

    pallet_no = fields.Char(string='No Pallet', tracking=True)

    # * time 
    start = fields.Char(string='Start Aktual', tracking=True)
    finish = fields.Char(string='Finish Aktual', tracking=True)
    
    # * first check
    first_check_code = fields.Char(string='Kode Body Botol', tracking=True)
    first_check_time = fields.Char(string='Jam pada Body Botol', tracking=True)
    first_check_count = fields.Char(string='No. of Counting Box', tracking=True)

    # * middle check
    middle_check_code = fields.Char(string='Kode Body Botol ', tracking=True)
    middle_check_time = fields.Char(string='Jam pada Body Botol ', tracking=True)
    middle_check_count = fields.Char(string='No. of Counting Box ', tracking=True)

    def _compute_total_output(self, ct, pcs):
        # ? should be configurable formula
        result = (ct * 36) + pcs
        return result

    # * qty pack/before banded
    qty_in_ct = fields.Float(string='CB', tracking=True)
    qty_in_pcs = fields.Float(string='pcs', tracking=True)
    total_output = fields.Float(string='Total Output', tracking=True)

    @api.onchange('qty_in_ct', 'qty_in_pcs')
    def _onchange_qty(self):
        value = {}
        value['total_output'] = self._compute_total_output(self.qty_in_ct, self.qty_in_pcs)
        return {'value': value}
    
    # @api.constrains('qty_in_ct', 'qty_in_pcs')
    # def _check_qty_pack(self):
    #     for record in self:
    #         if record.mrp_packing_id.packing_type == 'Filling':
    #             package = ' ' if not record.package_id else record.package_id.name
    #             if record.qty_in_ct != 0 and record.qty_in_pcs != 0:
    #                 warning = ' Qty CB dan Pcs tidak boleh diisi dua-duanya !'
    #                 if package:
    #                     warning = '[ No Urut Palet ' + package + ' ]' + warning
    #                 raise ValidationError(warning)
    
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

    def _get_uom_id(self, param):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        location_dest_id = int(get_param(param))
        return location_dest_id
        
    @api.onchange('uom_id', 'qty_in_ct', 'qty_in_pcs', 'qty_banded_in_ct', 'qty_banded_in_pcs')
    def _onchange_uom(self):
        value = {}
        qty_dict = {
            self.qty_in_ct: 'bmo_mrp_packing.bhp_cb_uom_id', 
            self.qty_in_pcs: 'bmo_mrp_packing.bhp_pcs_uom_id', 
            self.qty_banded_in_ct: 'bmo_mrp_packing.bhp_cb_uom_id', 
            self.qty_banded_in_pcs: 'bmo_mrp_packing.bhp_pcs_uom_id',
        }
        for k, v in qty_dict.items():
            if k > 0:
                value['uom_id'] = self._get_uom_id(v)
        return {'value': value}

    # * qty after banded
    qty_banded_in_ct = fields.Float(string='CB ', tracking=True)
    qty_banded_in_pcs = fields.Float(string='pcs ', tracking=True)
    total_output_banded = fields.Float(string='Total Output ', tracking=True)
    

    @api.onchange('qty_banded_in_ct', 'qty_banded_in_pcs')
    def _onchange_qty_banded(self):
        value = {}
        value['total_output'] = self._compute_total_output(self.qty_banded_in_ct, self.qty_banded_in_pcs)
        value['total_output_banded'] = self._compute_total_output(self.qty_banded_in_ct, self.qty_banded_in_pcs)
        return {'value': value}

    @api.constrains('qty_banded_in_ct', 'qty_banded_in_pcs')
    def _check_qty_banded(self):
        for record in self:
            package = ' ' if not record.package_id else record.package_id.name
            if record.qty_banded_in_ct != 0 and record.qty_banded_in_pcs != 0:
                warning = ' Qty CB dan Pcs tidak boleh diisi dua-duanya !'
                if package:
                    warning = '[ No Urut Palet ' + package + ' ]' + warning
                raise ValidationError(warning)

    # * PIC
    user_mrp_id = fields.Many2one('res.users', string='User PRD', 
        default=lambda self: self.env.uid, tracking=True)
    user_mrp = fields.Char(string='User PRD', tracking=True)
    user_whs_id = fields.Many2one('res.users', string='User WHS', tracking=True)
    user_whs = fields.Char(string='Operator', tracking=True)
    user_pack_id = fields.Many2one('res.users', string='User Release to WHS',
        default=lambda self: self.env.uid, tracking=True)
    history = fields.Datetime(string='Histori Waktu', tracking=True)

    # * product and location
    product_id = fields.Many2one('product.product', store=True, 
        related='mrp_packing_id.product_id')
    lot_producing_id = fields.Many2one('stock.production.lot', store=True,
        related='mrp_packing_id.lot_producing_id')
    expiration_date = fields.Datetime(related='lot_producing_id.expiration_date')

    product_status = fields.Boolean(string='Status Product', tracking=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type')
    location_id = fields.Many2one('stock.location', string='Location', 
        related='mrp_packing_id.location_dest_id')
        
    location_dest_ids = fields.Many2many('stock.location', string='Locators', compute='_get_loc_ids')

    @api.depends('location_dest_id')
    def _get_loc_ids(self):
        location_dest_ids = []
        for record in self:
            mrp_packing_line = record.mrp_packing_id.mrp_packing_line
            location_dest_ids = [x.location_dest_id.id for x \
                in mrp_packing_line if x.location_dest_id.id != False]
            location_dest_ids += set([x.location_id.id for x in mrp_packing_line])
            record.location_dest_ids = [(6, 0, location_dest_ids)]
            # print(record.location_dest_ids, "###LD###")
            # record.write({'location_dest_ids': [(6, 0, location_dest_ids)]})

    # def _get_location_dest_ids(self):
    #     active_id = self.env.context.get('active_id')
    #     active_model = self.env.context.get('active_model')
    #     payslip_id = self.env[active_model].browse(active_id)
    #     self.search([('mpr_packing_id', '=', self.mrp_packing_id.id)])
    #     return

    location_dest_id = fields.Many2one('stock.location', string='Locator')
    
    _sql_constraints = [
            ('bhp_locator_uniq', 'unique(location_dest_id, mrp_packing_id)', 
                'Locator sudah digunakan untuk BHP yang sama !'),
        ]
    
    production_id = fields.Many2one('mrp.production', 
        string='Production', tracking=True)
    location_src_id = fields.Many2one('stock.location', string='Source Location',
        related='mrp_packing_id.location_src_id')
    picking_id = fields.Many2one('stock.picking', string='Transfer')
    packing_type = fields.Selection(related='mrp_packing_id.packing_type')
    move_line_id = fields.Many2one('stock.move.line', string='Operations')
    is_revision = fields.Boolean(string='Revision')
    okp_id = fields.Many2one('mrp.okp', related='mrp_packing_id.okp_id', store=True)
    state_picking = fields.Char(compute='_compute_state_picking', string='Status Picking', store=True)
    batch_mrp_id = fields.Many2one("batch.mrp.production", "Batch MRP", compute="_compute_mrp_batch")
    state_mrp = fields.Char(compute='_compute_mrp_batch', string='Status MRP')
    state_sortir = fields.Char(compute='_compute_state_sortir', string='Status Sortir')
    
    def _compute_mrp_batch(self):
        for rec in self:
            rec.batch_mrp_id = self.env['batch.mrp.production'].search([('okp_id','=',rec.okp_id.id),('product_id','=',rec.product_id.id),('state','!=','cancel')], limit=1).id or False
            state_mrp_list = []
            for mrp in rec.batch_mrp_id.mrp_line.filtered(lambda l : l.state != 'cancel'):
                if mrp.state not in state_mrp_list:
                    state_mrp_list.append(mrp.state)
            if not state_mrp_list:
                state_mrp = "Open"
            elif 'done' in state_mrp_list and len(state_mrp_list) == 1:
                state_mrp = "Done"
            else:
                state_mrp = "In Progres"
            
            rec.state_mrp = state_mrp
    
    def _compute_state_sortir(self):
        for rec in self:
            mr_src = self.env['material.purchase.requisition'].search([('okp_id.okp_id','=',rec.okp_id.id),('state','not in',('cancel','reject'))])
            rec.state_sortir = self.env['stock.picking'].search([('custom_requisition_id','in',mr_src.ids),('state','!=','cancel')],limit=1).state or ''
    
    @api.depends('picking_id','picking_id.state')
    def _compute_state_picking(self):
        for rec in self:
            if rec.picking_id:
                rec.state_picking = rec.picking_id.state
            else:
                rec.state_picking = ''
    
    def action_done(self):
        for record in self:
            total_output = record.total_output or record.total_output_banded
            record.mrp_packing_id.total_output = total_output
        return self.write({'is_revision': False, 'state': 'done'})

    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref('bmo_mrp_packing.mrp_packing_line_view_form')
        return {
            'name': 'Detail BHP',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mrp.production.packing.line',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id
        }

    def action_revisi(self):
        # for record in self:
        #     print(record.picking_id, "### picking_id - action_revisi ###")
        #     print(x)
        return self.write({'is_revision': True, 'state': 'in_progress'})
    
    def unlink(self):
        # Add code here
        for record in self:
            if record.move_line_id:
                raise ValidationError('Cannot delete this data, Stock Move already created !')
        return super(MrpProductonPackingLine, self).unlink()

    def action_write_picking(self, records, picking_id, qty):
        for record in records:
            vals = {'state': 'done', 'picking_id': picking_id,
                'history': fields.Datetime.now(), 'product_status': True}
            record.write(vals)
    
    def action_release(self):
        qty = 0
        records = []
        move_id = False
        picking_id = False
        for record in self:
            if record.mrp_packing_state != 'done':
                raise ValidationError('Proses BHP pada Production belum selesai !')

            if not record.location_dest_id and not record.user_whs:
                raise ValidationError('Locator dan Operator wajib diisi !')

            if record.picking_id:
                raise ValidationError('Transfer sudah Ada !')

            if not picking_id:
                res = record.action_create_picking()
                move_id = False if not res else res['move_id']
                picking_id = False if not res else res['picking_id']
            # * write move line package
            # record.write_move_line(record, move_id)
            if not record.picking_id:
                records.append(record)
        
            # qty += record.total_output or record.total_output_banded
            if record.packing_type == 'Banded':
                qty += record.total_output_banded
            else:
                qty += record.total_output
                
        # print(qty, "###Q###")
        # print(x)
        if move_id:
            move_id.product_uom_qty = qty
        # print(move_id.product_uom_qty, "###product_uom_qty###")
        # print(x)

        return self.action_write_picking(records, picking_id, qty)

    def write_move_line(self, record, move_id):
        qty_done = record.total_output if not \
            record.total_output_banded else record.total_output_banded
        if record.packing_type == 'Banded':
            qty_done = record.qty_in_ct
        move_line_obj = self.env['stock.move.line']
        move_line_vals = {
                'lot_id': record.mrp_packing_id.lot_producing_id.id,
                'product_id': record.mrp_packing_id.product_id.id,
                'location_id': record.location_src_id.id,
                'location_dest_id': record.location_dest_id.id,
                'company_id': self.env.user.company_id.id,
                # 'product_uom_id': record.mrp_packing_id.product_id.uom_id.id,
                'product_uom_id': record.uom_id.id if record.uom_id \
                    else record.mrp_packing_id.product_id.uom_id.id,
                'qty_done': qty_done,
                # 'package_id': record.package_id.id,
                'result_package_id': record.package_id.id,
                'move_id': move_id.id
            }
        quarantine = True if record.mrp_packing_id.packing_type == 'Banded' else False
        record.location_dest_id.quarantine = quarantine
        move_line_id = move_line_obj.sudo().create(move_line_vals)
        # record.sudo().write({'move_line_id': move_line_id.id})
        return True
    
    @api.model
    def _prepare_pick_vals(self, record=False, picking_id=False):
        qty_done = record.total_output
        if record.packing_type == 'Banded':
            # qty_done = record.qty_in_ct
            qty_done = record.total_output_banded
        pick_vals = {
            'name': record.name,
            'picking_id': picking_id.id,
            'product_id': record.product_id.id,
            'location_id': record.location_src_id.id,
            'company_id': self.env.user.company_id.id,
            'product_uom': record.product_id.uom_id.id,
            'location_dest_id': record.location_dest_id.id,
            'picking_type_id': record.mrp_packing_id.picking_type_id.id,
            'product_uom_qty': qty_done,
        }
        print(pick_vals, "###pick_vals###")
        return pick_vals

    def action_create_picking(self):
        move_id = False
        picking_id = False
        for record in self:
            pick_obj = self.env['stock.picking']
            move_obj = self.env['stock.move']
            mrp_line = record.mrp_packing_id.batch_mrp_id.mrp_line
            location_src_id = [x.location_dest_id.id for x in mrp_line]
            if not location_src_id:
                raise ValidationError('Invalid Source Location, please check related Batch MRP !')
            record.mrp_packing_id.location_src_id = location_src_id[0]
            picking_vals = {
                'partner_id': self.env.user.partner_id.id,
                'location_id': record.mrp_packing_id.location_src_id.id,
                'location_dest_id': record.mrp_packing_id.location_dest_id.id,
                'picking_type_id': record.mrp_packing_id.picking_type_id.id,
                'note': record.mrp_packing_id.name,
                'origin': record.mrp_packing_id.name,
                'company_id': self.env.user.company_id.id,
            }
            picking_id = pick_obj.sudo().create(picking_vals)
            pick_vals = record._prepare_pick_vals(record, picking_id)
            move_id = move_obj.sudo().create(pick_vals)        
        result = {'move_id': move_id, 'picking_id' : picking_id.id}
        return result

    def action_hold(self):
        return self.write({'state': 'hold'})

    def action_reject(self):
        # ToDo: update reject in OKP
        for record in self:
            if not record.mrp_packing_id:
                raise ValidationError('Please save the form first !')
            batch_ids = record.mrp_packing_id._get_batch_mrp(\
                record.mrp_packing_id.okp_id, record.packing_type)
            # print(record.mrp_packing_id.okp_id, record.packing_type, "###P###")
            # print(batch_ids, "###BI###")
            scrap_obj = self.env['stock.scrap']
            for batch in batch_ids:
                for mrp in batch.mrp_line.filtered(lambda x: x.tipe == record.packing_type):
                    # print(mrp, "###M###")
                    # print(mrp.reject_qty, "###R1###")
                    mrp.reject_qty += record.total_output
                    # print(mrp.reject_qty, "###R2###")
                    # scrap_id = scrap_obj.with_context(active_model='mrp.production', \
                    #     active_id=mrp.id).create({
                    scrap_id = scrap_obj.create({
                            'product_id': record.mrp_packing_id.product_id.id, 
                            'scrap_qty': record.total_output or record.total_output_banded, 
                            'product_uom_id': record.uom_id.id, 
                            'location_id': mrp.location_src_id.id, 
                            'lot_id': record.mrp_packing_id.lot_producing_id.id, 
                            'production_id': mrp.id
                        })
                    print(scrap_id if not scrap_id else scrap_id.name, "###S###")
        return self.write({'state': 'reject'})

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_assign(self):
        quant_obj = self.env['stock.quant']
        for rec in self:
            src_bhp = self.env['mrp.production.packing.line'].search([('picking_id','=',rec.id)])
            if src_bhp:
                src_bhp._compute_state_picking()
                for move in rec.move_ids_without_package:
                    for bhp in src_bhp:
                        if bhp.packing_type == 'Filling': 
                            qty_bhp = bhp.total_output
                        if bhp.packing_type == 'Banded':
                            qty_bhp = bhp.total_output_banded
                        location_id = move.location_id
                        # src_lot = self.env['stock.production.lot'].search([('name','=',bhp.lot_producing_id.name)])
                        # lot_id = self.env['stock.quant'].search([('lot_id','in',src_lot.ids),('location_id','=',location_id.id)],limit=1).lot_id
                        lot_id = bhp.lot_producing_id
                        forced_package_id = move.package_level_id.package_id or None
                        available_quantity = move.sudo()._get_available_quantity(location_id, package_id=forced_package_id)
                        if available_quantity <= 0:
                            continue
                        taken_quantity = move._update_reserved_quantity_bhp_kmi(qty_bhp, min(qty_bhp, available_quantity), location_id, lot_id=lot_id, package_id=False, result_package_id=False, bhp=bhp, strict=True)
        return super(StockPicking, self).action_assign()
    
    def button_validate(self):
        for rec in self:
            src_bhp = self.env['mrp.production.packing.line'].search([('picking_id','=',rec.id)])
            if src_bhp:
                src_bhp._compute_state_picking()
            return super(StockPicking, self).button_validate()

class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals_bhp_kmi(self, quantity=None, reserved_quant=None, bhp=None):
        self.ensure_one()
        packang = self.env['stock.quant.package'].search([('location_id','=','bhp.package_id.id')], limit=1)
        if not packang:
            packang = self.env['stock.quant.package'].create({'name' : bhp.package_id.name})
        vals = {
            'move_id': self.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': bhp.location_dest_id.id,
            'picking_id': self.picking_id.id,
            'company_id': self.company_id.id,
            'result_package_id': packang.id,
        }
        if quantity:
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom, rounding_method='HALF-UP')
            vals = dict(vals, product_uom_qty=uom_quantity, product_uom_id=self.product_uom.id, package_id=False, result_package_id=packang.id)
        if reserved_quant:
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                package_id=False or False,
                result_package_id=packang.id or False,
                owner_id =reserved_quant.owner_id.id or False,
            )
        return vals

    def _update_reserved_quantity_bhp_kmi(self, need, available_quantity, location_id, lot_id=None, package_id=None, result_package_id=None, owner_id=None, bhp=None, strict=None):
        """ Create or update move lines.
        """
        self.ensure_one()

        if not lot_id:
            lot_id = self.env['stock.production.lot']
        if not package_id:
            package_id = self.env['stock.quant.package']
        if not owner_id:
            owner_id = self.env['res.partner']
        taken_quantity = min(available_quantity, need)
        quants = []

        try:
            with self.env.cr.savepoint():
                if not float_is_zero(taken_quantity, precision_rounding=self.product_id.uom_id.rounding):
                    quants = self.env['stock.quant'].sudo()._update_reserved_quantity(
                        self.product_id, location_id, taken_quantity, lot_id=lot_id,
                        package_id=package_id, owner_id=owner_id, strict=strict
                    )
        except UserError:
            taken_quantity = 0
        if taken_quantity <= 0:
            raise ValidationError(_("Produck Belum ada di Gudang"))
        for reserved_quant, quantity in quants:
            self.env['stock.move.line'].create(self._prepare_move_line_vals_bhp_kmi(quantity=quantity, reserved_quant=reserved_quant, bhp=bhp))
        return taken_quantity
