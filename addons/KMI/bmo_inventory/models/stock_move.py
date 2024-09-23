# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.tools.misc import format_date, OrderedSet

class StockMove(models.Model):
    _inherit = 'stock.move'

    vendor_id = fields.Many2one("res.partner", string='Vendor')
    product_uom_qty_origin = fields.Float(
        'Demand Origin', digits='Product Unit of Measure', default=0.0, copy=False)


    def do_unreserve(self):
        for move in self:
            product_uom_qty = move.product_uom_qty
            move_line_ids = move.mapped('move_line_ids').write({'qty_done' : 0})
            move._do_unreserve()
            move.product_uom_qty = product_uom_qty

    @api.depends('product_id', 'has_tracking', 'move_line_ids')
    def _compute_show_details_visible(self):
        """ According to this field, the button that calls `action_show_details` will be displayed
        to work on a move from its picking form view, or not.
        """
        has_package = self.user_has_groups('stock.group_tracking_lot')
        multi_locations_enabled = self.user_has_groups('stock.group_stock_multi_locations')
        consignment_enabled = self.user_has_groups('stock.group_tracking_owner')

        show_details_visible = multi_locations_enabled or has_package

        for move in self:
            move.show_details_visible = True

            # Kondisi elif dan else itu dikomen karena ga tau harusnya pake kondisi yang seperti apa T_T
            if not move.product_id:
                move.show_details_visible = False
            # elif len(move.move_line_ids) > 1:
            # 	move.show_details_visible = True
            # else:
            # 	move.show_details_visible = (((consignment_enabled and move.picking_id.picking_type_id.code != 'incoming') or
            # 								 show_details_visible or move.has_tracking != 'none') and
            # 								 move._show_details_in_draft() and
            # 								 move.picking_id.picking_type_id.show_operations is False)

    def action_view_quants(self):
        action = self.env.ref('bmo_inventory.action_wizard_tags_location').sudo().read()[0]
        return action


    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(StockMove, self).onchange_product_id()
        if self.picking_id.picking_type_code == 'incoming':
            product = self.product_id.with_context(lang=self._get_lang())
            self.product_uom = product.uom_po_id.id

        return res

    def action_back_to_draft(self):
        self._do_unreserve()
        self.write({"state": "draft"})
        
    def action_show_details(self):
        res = super(StockMove, self).action_show_details()
        for rec in self:
            if rec.picking_id.picking_type_code == 'incoming' and not rec.picking_id.delivery_return:
                res['context']['show_lots_m2o'] = False
                res['context']['show_lots_text'] = True
        return res
    
    @api.depends('state', 'picking_id')
    def _compute_is_initial_demand_editable(self):
        for move in self:
            if move.state == 'draft':
                move.is_initial_demand_editable = True
            elif not move.picking_id.is_locked and move.state != 'done' and move.picking_id:
                move.is_initial_demand_editable = True
            else:
                move.is_initial_demand_editable = False

    def _prepare_move_line_vals_manual_kmi(self, quantity=None, reserved_quant=None, quant=None):
        self.ensure_one()
        # apply putaway
        location_dest_id = self.location_dest_id._get_putaway_strategy(self.product_id).id or self.location_dest_id.id
        vals = {
            'move_id': self.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'location_id': self.location_id.id,
            'location_dest_id': location_dest_id,
            'picking_id': self.picking_id.id,
            'company_id': self.company_id.id,
        }
        if quantity:
            uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom, rounding_method='HALF-UP')
            vals = dict(vals, product_uom_qty=uom_quantity, product_uom_id=self.product_uom.id, qty_done=uom_quantity)
        if reserved_quant:
            vals = dict(
                vals,
                location_id=reserved_quant.location_id.id,
                lot_id=reserved_quant.lot_id.id or False,
                package_id=reserved_quant.package_id.id or False,
                owner_id =reserved_quant.owner_id.id or False,
            )
        if self.product_id.type == 'consu':
            vals = dict(vals, qty_done=quantity)
        return vals

    def _update_reserved_quantity_manual_kmi(self, need, available_quantity, location_id, lot_id=None, package_id=None, owner_id=None, quant=None, strict=True):
        self.ensure_one()

        if not lot_id:
            lot_id = self.env['stock.production.lot']
        if not package_id:
            package_id = self.env['stock.quant.package']
        if not owner_id:
            owner_id = self.env['res.partner']
        taken_quantity = min(available_quantity, need)
        quants = []
        if self.product_id.tracking == 'serial':
            rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare(taken_quantity, int(taken_quantity), precision_digits=rounding) != 0:
                taken_quantity = 0

        if not float_is_zero(taken_quantity, precision_rounding=self.product_id.uom_id.rounding):
            quants = self.env['stock.quant']._update_reserved_quantity_by_id(
                self.product_id, location_id, taken_quantity, lot_id=lot_id,
                package_id=package_id, owner_id=owner_id, strict=strict, quant_id=quant
            )
        else:
            taken_quantity = 0

        for reserved_quant, quantity in quants:
            self.env['stock.move.line'].create(self._prepare_move_line_vals_manual_kmi(quantity=quantity, reserved_quant=reserved_quant, quant=quant))
        return taken_quantity
    