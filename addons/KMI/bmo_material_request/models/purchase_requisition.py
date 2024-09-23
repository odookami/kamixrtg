# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date
from odoo.exceptions import Warning, UserError
from odoo.addons.bmo_mrp.models.product import state_tipe


class MaterialPurchaseRequisition(models.Model):
    _name = 'material.purchase.requisition'
    _description = 'Purchase Requisition'
    #_inherit = ['mail.thread', 'ir.needaction_mixin']
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']      # odoo11
    _order = 'id desc'
    
    #@api.multi
    def unlink(self):
        for rec in self:
            if rec.state not in ('draft', 'cancel', 'reject'):
                raise Warning(_('You can not delete Material Request which is not in draft or cancelled or rejected state.'))
        return super(MaterialPurchaseRequisition, self).unlink()
    
    @api.model
    def _default_location_id(self):
        setting = self.env['res.company']._company_default_get('material.settings')
        location_id = setting.location_id
        return location_id
    
    @api.model
    def _default_dest_location_id(self):
        setting = self.env['res.company']._company_default_get('material.settings')
        dest_location_id = setting.dest_location_id
        return dest_location_id
    
    @api.model
    def _default_picking_type_id(self):
        setting = self.env['res.company']._company_default_get('material.settings')
        picking_type_id = setting.picking_type_id
        return picking_type_id
    
    @api.model
    def _default_product_special(self):
        config = self.env['config.special.product'].search([], limit=1).id
        return config

    name = fields.Char(
        string='Number',
        index=True,
        readonly=1,
    )
    state = fields.Selection([
        ('draft', 'New'),
        ('dept_confirm', 'Waiting Department Approval'),
        ('ir_approve', 'Waiting IR Approval'),
        ('approve', 'Confirm'),
        ('stock', 'Requested'),
        ('receive', 'Received'),
        ('cancel', 'Cancelled'),
        ('reject', 'Rejected')],
        default='draft',
        tracking=True,
    )
    request_date = fields.Date(
        # string='Requisition Date',
        string='Request Date',
        default=fields.Date.context_today,
        required=True,
    )
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        copy=True,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1),
        copy=True,
    )
    approve_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager',
        readonly=True,
        copy=False,
    )
    reject_manager_id = fields.Many2one(
        'hr.employee',
        string='Department Manager Reject',
        readonly=True,
    )
    approve_employee_id = fields.Many2one(
        'hr.employee',
        string='Approved by',
        readonly=True,
        copy=False,
    )
    reject_employee_id = fields.Many2one(
        'hr.employee',
        string='Rejected by',
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.user.company_id,
        required=True,
        copy=True,
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        copy=True, default=_default_location_id
    )
    requisition_line_ids = fields.One2many(
        'material.purchase.requisition.line',
        'requisition_id',
        # string='Purchase Requisitions Line',
        string='Material Request Line',
        copy=True,
    )
    date_end = fields.Date(
        # string='Requisition Deadline', 
        string='Deadline', 
        readonly=True,
        help='Last date for the product to be needed',
        copy=True,
    )
    date_done = fields.Date(
        string='Date Done', 
        readonly=True, 
        help='Date of Completion of Purchase Requisition',
    )
    managerapp_date = fields.Date(
        string='Department Approval Date',
        readonly=True,
        copy=False,
    )
    manareject_date = fields.Date(
        string='Department Manager Reject Date',
        readonly=True,
    )
    userreject_date = fields.Date(
        string='Rejected Date',
        readonly=True,
        copy=False,
    )
    userrapp_date = fields.Date(
        string='Approved Date',
        readonly=True,
        copy=False,
    )
    receive_date = fields.Date(
        string='Received Date',
        readonly=True,
        copy=False,
    )
    reason = fields.Text(
        string='Reason for Requisitions',
        required=False,
        copy=True,
    )
    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account',
        copy=True,
    )
    dest_location_id = fields.Many2one(
        'stock.location',
        string='Destination Location',
        required=False,
        copy=True, default=_default_dest_location_id
    )
    delivery_picking_id = fields.Many2one(
        'stock.picking',
        string='Internal Picking',
        readonly=True,
        copy=False,
    )
    delivery_picking_ids = fields.Many2many(
        'stock.picking',
        string='Internal Picking',
        readonly=True,
        copy=False,
    )
    requisiton_responsible_id = fields.Many2one(
        'hr.employee',
        # string='Requisition Responsible',
        string='Responsible',
        copy=True,
    )
    employee_confirm_id = fields.Many2one(
        'hr.employee',
        string='Confirmed by',
        readonly=True,
        copy=False,
    )
    confirm_date = fields.Date(
        string='Confirmed Date',
        readonly=True,
        copy=False,
    )
    custom_picking_type_id = fields.Many2one(
        'stock.picking.type',
        string='Picking Type',
        copy=False, default=_default_picking_type_id
    )
    tipe = fields.Selection(
        state_tipe, string='Type OKP', tracking=True)
    # * mo / okp
    batch_production_id = fields.Many2one(
        'batch.mrp.production', string='OKP', copy=False)
    product_batch_id = fields.Many2one(
        "product.product", "Product", related="batch_production_id.product_id")
    batch_proses = fields.Float(
        string='Batch Proses', related="batch_production_id.batch_proses")
    uom_id = fields.Many2one(
        'uom.uom',
        string='Standar Formulasi',
        related="batch_production_id.bom_id.product_uom_id",
    )
    conf_special_product_id = fields.Many2one(
        "config.special.product", string="Special Product", default=_default_product_special)
    product_product_ids = fields.Many2many(
        "product.product", string="Product Conf", related="conf_special_product_id.product_ids", sote=True)
    mo_id = fields.Many2one(
        "mrp.production", "Manufacturing Orders")
    okp_id = fields.Many2one(
        'batch.mrp.production', string='OKP Sortir', copy=False)

    @api.onchange('state')
    def _onchange_okp_id(self):
        bhp_src = self.env['mrp.production.packing.line'].search([('packing_type','=','Filling'),('state_picking','=','done')]).mapped('okp_id')
        return {'domain' : { 'okp_id' : [('okp_id','in', bhp_src.ids),('state','in',['progress','done']),('product_id','in',self.product_product_ids.ids)] }}

    @api.onchange('batch_production_id','okp_id')
    def _onchange_batch_production_id(self):
        lines = []
        lines_dict = {}
        if self.batch_production_id:
            # self.batch_proses = self.batch_production_id.batch_proses
            self.okp_id = False
            for mrp in self.batch_production_id.mrp_line:
                for move in mrp.move_raw_ids:
                    if move.product_id.id not in lines_dict:
                        lines_dict[move.product_id.id] = {move.product_uom.id:[move.product_uom_qty]}
                    else:
                        if move.product_uom.id not in lines_dict[move.product_id.id]:
                            lines_dict[move.product_id.id][move.product_uom.id] = [move.product_uom_qty]
                        else:
                            if move.product_uom.id in lines_dict[move.product_id.id]:
                                if move.product_uom.id not in lines_dict[move.product_id.id][move.product_uom.id]:
                                    lines_dict[move.product_id.id][move.product_uom.id].append(move.product_uom_qty)
            for k, v in lines_dict.items():
                product = self.env['product.product'].browse(k)
                bom = self.env['mrp.bom'].search([('product_tmpl_id','=',product.product_tmpl_id.id)])
                if product.type == 'product' and not bom:
                    for x, y in v.items():
                        uom = self.env['uom.uom'].browse(x)
                        qty = sum(y)
                        lines.append((0,0,{
                            'requisition_id': self.id,
                            'product_id'    : product.id,
                            'description'   : product.display_name,
                            'uom'           : uom.id,
                            'qty'           : qty,
                        })) 
        if self.okp_id:
            self.tipe = False
            self.batch_production_id = False
            conf = self.env['master.default.location'].search([('config_id','=',self.conf_special_product_id.id),('sequence_ref','=','1')], limit=1)
            bhp_src = self.env['mrp.production.packing.line'].search([('okp_id','=',self.okp_id.okp_id.id),('product_id','=',self.okp_id.product_id.id),('state_picking','=','done')])
            for x in bhp_src:
                if x.product_id.id not in lines_dict:
                    lines_dict[x.product_id.id] = {x.lot_producing_id.id:[x.total_output]}
                else:
                    if x.lot_producing_id.id not in lines_dict[x.product_id.id]:
                        lines_dict[x.product_id.id][x.lot_producing_id.id] = [x.lot_producing_id]
                    else:
                        if x.lot_producing_id.id in lines_dict[x.product_id.id]:
                            if x.lot_producing_id.id not in lines_dict[x.product_id.id][x.lot_producing_id.id]:
                                lines_dict[x.product_id.id][x.lot_producing_id.id].append(x.total_output)
            for k, v in lines_dict.items():
                product = self.env['product.product'].browse(k)
                if product.type == 'product':
                    for x, y in v.items():
                        qty = sum(y)
                        lines.append((0,0,{
                            'requisition_id'    : self.id,
                            'product_id'        : product.id,
                            'description'       : product.display_name,
                            'uom'               : product.uom_id.id,
                            'qty'               : qty,
                            'lot_producing_id'  : x,
                        }))
        self.requisition_line_ids = False
        value = {'requisition_line_ids': lines} if lines else {}
        return {'value': value}
    
    @api.onchange('tipe')
    def _onchange_tipe(self):
        for rec in self:
            master_domain = self.env['master.default.location'].search([('tipe','=',rec.tipe)])
            if master_domain:
                for m in master_domain:
                    rec.location_id = m.location_id.id or False
                    rec.dest_location_id = m.dest_location_id.id or False
                    rec.custom_picking_type_id = m.picking_type_id.id or False

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('material.request.seq')
        vals.update({
            'name': name
            })
        res = super(MaterialPurchaseRequisition, self).create(vals)
        return res
        
    def requisition_confirm(self):
        for rec in self:
            manager_mail_template = self.env.ref('bmo_material_request.email_confirm_material_purchase_requistion')
            setting = self.env['res.company']._company_default_get('material.settings').users_ids
            if self.env.user.id not in setting.ids:
                notification_ids = []
                body = f'User {self.env.user.name} Membuat MR dengan Number {self.name}'
                for user in setting:
                    notification_ids.append((0,0,{
                        'res_partner_id':user.partner_id.id,
                        'notification_type':'inbox'}))
                self.message_post(body=body, message_type='notification', author_id=self.env.user.partner_id.id, notification_ids=notification_ids)
            rec.employee_confirm_id = rec.employee_id.id
            rec.confirm_date = fields.Date.today()
            rec.state = 'approve'
    #@api.multi
    def requisition_reject(self):
        for rec in self:
            rec.state = 'reject'
            rec.reject_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.userreject_date = fields.Date.today()

    #@api.multi
    def manager_approve(self):
        for rec in self:
            rec.state = 'ir_approve'

    #@api.multi
    def user_approve(self):
        for rec in self:
            rec.userrapp_date = fields.Date.today()
            rec.approve_employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.state = 'approve'

    #@api.multi
    def reset_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_assign(self):
        for record in self:
            locations = self.env["stock.location"].search(
                [("id", "child_of", [record.location_id.id])]
            )
            for line in record.requisition_line_ids:
                quant_obj = self.env['stock.quant']
                domain = [('product_id', '=', line.product_id.id),('location_id', 'in', tuple(locations.ids))]
                quant_ids = quant_obj.search(domain)
                qty = sum([x.available_quantity for x in quant_ids])
                if qty >= line.qty:
                    line.is_available = True
                else:
                    line.is_available = False
        return True

    @api.model
    def _picking_vals(self, data_conf=False):
        location_id = self.location_id.id
        dest_location_id = self.dest_location_id.id
        custom_picking_type_id = self.custom_picking_type_id.id
        batch_production_id = self.batch_production_id.id
        if data_conf:
            location_id = data_conf.location_id.id
            dest_location_id = data_conf.dest_location_id.id
            custom_picking_type_id = data_conf.picking_type_id.id
            batch_production_id = self.okp_id.id
        picking_vals = {
            'partner_id'            : self.employee_id.sudo().address_home_id.id,
            'location_id'           : location_id,
            'location_dest_id'      : dest_location_id,
            'picking_type_id'       : custom_picking_type_id,
            'note'                  : self.reason,
            'custom_requisition_id' : self.id,
            'origin'                : self.name,
            'company_id'            : self.company_id.id,
            'tipe'                  : self.tipe or False,
            'batch_production_id'   : batch_production_id,
        }
        return picking_vals

    @api.model
    def _prepare_pick_vals(self, line=False, stock_id=False, data_conf=False):
        location_id = self.location_id.id
        dest_location_id = self.dest_location_id.id
        custom_picking_type_id = self.custom_picking_type_id.id
        mo_id = False
        lot_producing_id = False
        qty = line.qty
        uom = line.uom.id
        company_id = line.requisition_id.company_id.id
        custom_requisition_line_id = line.id
        if data_conf:
            location_id = data_conf.location_id.id
            dest_location_id = data_conf.dest_location_id.id
            custom_picking_type_id = data_conf.picking_type_id.id
        pick_vals = {
            'product_id'                : line.product_id.id,
            'product_uom_qty'           : qty,
            'product_uom'               : uom,
            'location_id'               : location_id,
            'location_dest_id'          : dest_location_id,
            'name'                      : line.product_id.name,
            'picking_type_id'           : custom_picking_type_id,
            'picking_id'                : stock_id.id,
            'custom_requisition_line_id': custom_requisition_line_id,
            'company_id'                : company_id,
            'mo_id'                     : mo_id,
        }
        return pick_vals
    
    def _move_line_nosuggest(self, line, location_id=False, dest_location_id=False):
        move_line = [(0, 0, {
            'product_id'        : line.product_id.id,
            'product_uom_id'    : line.uom.id,
            'location_id'       : location_id.id,
            'location_dest_id'  : dest_location_id.id,
            'qty_done'          : line.qty,
            'lot_id'            : line.lot_producing_id.id,
        })]
        return move_line

    def request_stock(self):
        stock_obj = self.env['stock.picking']
        move_obj = self.env['stock.move']
        for rec in self:
            if not rec.location_id.id:
                raise Warning(_('Select Source location under the picking details.'))
            if not rec.custom_picking_type_id.id:
                raise Warning(_('Select Picking Type under the picking details.'))
            if not rec.dest_location_id:
                raise Warning(_('Select Destination location under the picking details.'))
            if not rec.requisition_line_ids:
                raise Warning(_('Please create some requisition lines.'))
            if any(line.requisition_type =='internal' for line in rec.requisition_line_ids):
                if rec.okp_id:
                    for x in rec.conf_special_product_id.config_line:
                        picking_vals = rec._picking_vals(x)
                        stock_id = stock_obj.sudo().create(picking_vals)
                        delivery_vals = {'delivery_picking_ids' :  [(4, stock_id.id)]}
                        rec.write(delivery_vals)     
                        for line in rec.requisition_line_ids:
                            pick_vals = rec._prepare_pick_vals(line, stock_id, x)
                            move_id = move_obj.sudo().create(pick_vals)
                else:
                    picking_vals = rec._picking_vals()
                    stock_id = stock_obj.sudo().create(picking_vals)
                    delivery_vals = {'delivery_picking_ids' :  [(4, stock_id.id)]}
                    rec.write(delivery_vals)     
                    for line in rec.requisition_line_ids:
                        pick_vals = rec._prepare_pick_vals(line, stock_id)
                        move_id = move_obj.sudo().create(pick_vals)
            rec.state = 'stock'
    
    #@api.multi
    def action_received(self):
        for rec in self:
            # check availability first
            rec.action_assign()
            rec.receive_date = fields.Date.today()
            rec.state = 'receive'
    
    #@api.multi
    def action_cancel(self):
        for rec in self:
            for p in rec.delivery_picking_ids:
                p.action_cancel()
            rec.state = 'cancel'

    #@api.multi
    def show_picking(self):
        for rec in self:
            res = self.env.ref('stock.action_picking_tree_all')
            res = res.read()[0]
            res['domain'] = str([('custom_requisition_id','=',rec.id)])
        return res
        
    #@api.multi
    def action_show_po(self):
        for rec in self:
            purchase_action = self.env.ref('purchase.purchase_rfq')
            purchase_action = purchase_action.read()[0]
            purchase_action['domain'] = str([('custom_requisition_id','=',rec.id)])
        return purchase_action