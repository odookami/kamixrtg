from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import format_date, OrderedSet


class Wizard_Tags_Location(models.TransientModel):
    _name = 'wizard.tags.location'
    _description = 'Wizard Location'

    move_ids = fields.Many2many(
        "stock.move", string="Stock Move")
    product_id = fields.Many2one(
        "product.product", "Porduct")
    location_id = fields.Many2one(
        'stock.location', string='Source Location')
    stock_quant_ids = fields.Many2many(
        "stock.quant", string="Stock Quant")
    
    wizard_line = fields.One2many(
        'wizard.tags.location.line', 'wizard_id', string='Wizard Line')
    
    @api.onchange('stock_quant_ids')
    def _onchange_stock_quant_ids(self):
        for rec in self:
            data_quant = self.env['stock.quant'].search(
                [('product_id', '=', rec.product_id.id),('location_id.usage', '=', 'internal'),('location_id', 'child_of', rec.location_id.id),('location_id.quarantine', '=', False)])
            data_quant_tuple = [x.id for x in data_quant if x.available_quantity > 0]
            return {'domain':{'stock_quant_ids':[('id','in',tuple(data_quant_tuple)),('id','not in',rec.stock_quant_ids.ids)]}}

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        move_id = self.env['stock.move'].browse(self.env.context.get('active_id'))
        res['product_id'] = move_id.product_id.id
        res['location_id'] = move_id.location_id.id
        res['move_ids'] = [(6, 0, move_id.ids)]
        return res
    
    def check_line(self):
        for rec in self:
            data_dic = {}
            for line in rec.wizard_line:
                if line.stock_quant_id.lot_id.id not in data_dic:
                    data_dic[line.stock_quant_id.lot_id.id] = {'available_quantity' : [line.available_quantity],'qty_done' : [line.qty_done]}
                else:
                    data_dic[line.stock_quant_id.lot_id.id]['available_quantity'].append(line.available_quantity)
                    data_dic[line.stock_quant_id.lot_id.id]['qty_done'].append(line.qty_done)
            return data_dic

    def add_data(self):
        for rec in self:
            move = rec.move_ids[0]
            quantity_demand = move.product_uom_qty
            quantity_demand_copy = quantity_demand
            qty_done_move_line = sum(move.move_line_ids.mapped('qty_done'))

            if move.product_id.uom_id.id != move.product_uom.id:
                qty_done_move_line = move.product_id.uom_id._compute_quantity(qty_done_move_line, move.product_uom, rounding_method='HALF-UP')
                quantity_demand_copy = move.product_uom._compute_quantity(quantity_demand_copy, move.product_id.uom_id, rounding_method='HALF-UP')
            if not rec.stock_quant_ids and not rec.wizard_line:
                raise ValidationError(_("Mohon Isi Salah satu Line atau Cancel form"))

            if rec.stock_quant_ids:
                if move.quantity_done <= quantity_demand:
                    for quant in rec.stock_quant_ids:
                        request_qty = quantity_demand_copy - qty_done_move_line
                        # print(request_qty,'XXXXXXXXXXXXX',quantity_demand_copy,'###############')
                        # if move.product_id.uom_id.id != move.product_uom.id:
                        #     request_qty = move.product_uom._compute_quantity(request_qty, move.product_id.uom_id, rounding_method='HALF-UP')
                        # print(request_qty,"XXXXXXXXXXXXXx")
                        if request_qty > 0:
                            if request_qty > quant.available_quantity:
                                request_qty = quant.available_quantity
                            qty_done_move_line += move._update_reserved_quantity_manual_kmi(request_qty, request_qty, quant.location_id, lot_id=quant.lot_id, package_id=quant.package_id, quant=quant, strict=True)
                            if move.product_id.uom_id.id != move.product_uom.id:
                                qty_done_move_line = move.product_id.uom_id._compute_quantity(qty_done_move_line, move.product_uom, rounding_method='HALF-UP')
            # print(XXXXXXXXXXXXXXx)
            if rec.wizard_line:
                data_dic = self.check_line()
                for k, v in data_dic.items():
                    lot = self.env['stock.production.lot'].browse(k)
                    available_quant = sum([x for x in v['available_quantity']])
                    qty_done = sum([x for x in v['qty_done']])
                    if qty_done > available_quant:
                        raise UserError(_(f'Lot {lot.name} tidak Cukup'))
                request_qty = sum([x.qty_done for x in rec.wizard_line])
                sisa_qty = quantity_demand_copy - request_qty
                if move.picking_id and move.picking_id.tipe == 'Mixing' and sisa_qty < 0:
                    raise ValidationError(_("Type OKP 'Mixing' Reserved Tidak Boleh Melebihi Demand"))
                # if move.picking_id and move.picking_id.picking_type_id.code == 'outgoing' and qty_done > sisa_qty:
                #     raise ValidationError(_("DO, Reserved Tidak Boleh Melebihi Demand"))
                for line in rec.wizard_line:
                    qty_done_move_line += move._update_reserved_quantity_manual_kmi(line.qty_done, line.qty_done, line.stock_quant_id.location_id, lot_id=line.stock_quant_id.lot_id, package_id=line.stock_quant_id.package_id, quant=line.stock_quant_id, strict=True)
                    if move.product_id.uom_id.id != move.product_uom.id:
                        qty_done_move_line = move.product_id.uom_id._compute_quantity(qty_done_move_line, move.product_uom, rounding_method='HALF-UP')
            if move.picking_id and move.picking_id.tipe == 'Mixing' and qty_done_move_line > quantity_demand:
                raise ValidationError(_("Type OKP 'Mixing' Reserved Tidak Boleh Melebihi Demand"))
            # if move.picking_id and  move.picking_id.picking_type_id.code == 'outgoing' and qty_done_move_line > quantity_demand:
            #     raise ValidationError(_("DO, Reserved Tidak Boleh Melebihi Demand"))
            else:
                if move.product_uom_qty_origin <= 0.0:
                    move.product_uom_qty_origin = quantity_demand
            if qty_done_move_line > 0:
                if move.picking_id and move.picking_id.tipe and move.picking_id.tipe != 'Mixing':
                    move.write({'product_uom_qty' : qty_done_move_line})
                if not move.picking_id:
                    move.write({'product_uom_qty' : qty_done_move_line})
            if move.picking_id:
                move.picking_id.immediate_transfer = True
                move.picking_id._compute_state()

class Wizard_Tags_Location_line(models.TransientModel):
    _name = 'wizard.tags.location.line'
    _description = 'Wizard Location Line'

    wizard_id = fields.Many2one(
        comodel_name='wizard.tags.location', string='Wizard', required=True, ondelete='cascade')
    stock_quant_id = fields.Many2one(
        "stock.quant", string="Stock Quant")
    available_quantity = fields.Float("Available Quantity", related="stock_quant_id.available_quantity", digits=(30,4))
    uom_id = fields.Many2one("uom.uom", "UoM", related="stock_quant_id.product_uom_id")
    lot_id = fields.Many2one("stock.production.lot",'Lot', related="stock_quant_id.lot_id")
    location_id = fields.Many2one(
        'stock.location', 'Location', related="stock_quant_id.location_id")
    package_id = fields.Many2one(
        'stock.quant.package', 'Package', related="stock_quant_id.package_id")
    qty_done = fields.Float("Qty Done", digits=(30,4))

    @api.onchange('stock_quant_id')
    def _onchange_stock_quant_id(self):
        for rec in self:
            data_quant = self.env['stock.quant'].search(
                [('product_id', '=', rec.wizard_id.product_id.id),('location_id.usage', '=', 'internal'),('location_id', 'child_of', rec.wizard_id.location_id.id),('location_id.quarantine', '=', False)])
            data_quant_tuple = [x.id for x in data_quant if x.available_quantity > 0]
            return {'domain':{'stock_quant_id':[('id','in',tuple(data_quant_tuple))]}}