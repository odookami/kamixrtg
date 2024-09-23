# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from email.policy import default
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import OrderedSet
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # product_group_id = fields.Many2one('product.group', string='Premix',)
    move_line_ids = fields.One2many('stock.move.line', 'picking_id', 'Operations', copy=True)
    karantina = fields.Boolean(string='Karantina Lot?',)
    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id), ('karantina', '=', False)]", check_company=True)
    expired_date =  fields.Datetime(string='Expired Date', related='lot_id.expiration_date')
    # quant_id = fields.Many2one("stock.quant", "Stock Quant")
    product_qty = fields.Float(
        'Real Reserved Quantity', digits='Product Unit of Measure',
        compute='_compute_product_qty', inverse='_set_product_qty', store=True)
    check_sc = fields.Boolean(compute='_compute_check_sc', string='Check SC', store=True)
    exp_lot = fields.Date('Exp Sampling')
    lot_new = fields.Char('Lot Sampling')
    not_adjust = fields.Boolean(string='Penanda Tidak dihitung', default=False)
    
    @api.depends('location_id','location_dest_id')
    def _compute_check_sc(self):
        for rec in self:
            if rec.location_id and rec.location_dest_id and rec.location_id.id == rec.location_dest_id.id:
                rec.check_sc = False
            else:
                rec.check_sc = True
    

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        domain = False
        if self.picking_id.delivery_return:
            return_id = self.picking_id.picking_return_id.id
            picking_return = self.env['stock.picking'].search([('id','=', return_id)],limit=1)
            domain = {'lot_id':[('id', '=', picking_return.move_line_ids_without_package.lot_id.ids)],}
        return {'domain': domain}

    def action_view_quants(self):
        domain = [('product_id', '=', self.product_id.id),('location_id.usage', '=', 'internal')]
        action = self.env.ref('bmo_inventory.action_stock_quant_viewss').sudo().read()[0]
        action['domain'] = domain
        return action

    def _create_and_assign_production_lot(self):
        """ Creates and assign new production lots for move lines."""
        lot_vals = [{
            'company_id': ml.move_id.company_id.id,
            'name': ml.lot_name,
            'product_id': ml.product_id.id,
            'picking_id': ml.picking_id.id,
            'karantina' : True if ml.picking_id.picking_type_code == 'incoming' else False,
        } for ml in self]
        lots = self.env['stock.production.lot'].create(lot_vals)
        for ml, lot in zip(self, lots):
            ml._assign_production_lot(lot)

    @api.constrains('lot_id', 'product_id')
    def _check_lot_product(self):
        for line in self:
            if line.lot_id and line.product_id.id != line.lot_id.sudo().product_id.id:
                raise ValidationError(_(
                    'This lot %(lot_name)s is incompatible with this product %(product_name)s',
                    lot_name=line.lot_id.name,
                    product_name=line.product_id.display_name
                ))
                
    # @api.onchange('product_id', 'product_uom_id')
    # def _onchange_product_id(self):
    #     res = super(StockMoveLine, self)._onchange_product_id()
    #     if self.picking_type_use_create_lots:
    #         if self.product_id.use_expiration_date:
    #             self.expiration_date = fields.Datetime.today() + datetime.timedelta(months=self.product_id.expiration_month)
    #         else:
    #             self.expiration_date = False
    #     return res

    def action_cancel_picking_arcive(self):
        for rec in self:
            if rec.picking_id and rec.picking_id.active == False and rec.state == 'done':
                rec.state = 'cancel'

    @api.constrains('product_uom_qty')
    def _check_reserved_done_quantity(self):
        for move_line in self:
            if move_line.state == 'done' and not float_is_zero(move_line.product_uom_qty, precision_digits=self.env['decimal.precision'].precision_get('Product Unit of Measure')):
                raise ValidationError(_('A done move line should never have a reserved quantity. product name %s') % (move_line.product_id.name))

    def _action_done(self):
        """ This method is called during a move's `action_done`. It'll actually move a quant from
        the source location to the destination location, and unreserve if needed in the source
        location.

        This method is intended to be called on all the move lines of a move. This method is not
        intended to be called when editing a `done` move (that's what the override of `write` here
        is done.
        """
        Quant = self.env['stock.quant']

        # First, we loop over all the move lines to do a preliminary check: `qty_done` should not
        # be negative and, according to the presence of a picking type or a linked inventory
        # adjustment, enforce some rules on the `lot_id` field. If `qty_done` is null, we unlink
        # the line. It is mandatory in order to free the reservation and correctly apply
        # `action_done` on the next move lines.
        ml_ids_tracked_without_lot = OrderedSet()
        ml_ids_to_delete = OrderedSet()
        ml_ids_to_create_lot = OrderedSet()
        for ml in self:
            ml._compute_check_sc()
            # Check here if `ml.qty_done` respects the rounding of `ml.product_uom_id`.
            uom_qty = float_round(ml.qty_done, precision_rounding=ml.product_uom_id.rounding, rounding_method='HALF-UP')
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            qty_done = float_round(ml.qty_done, precision_digits=precision_digits, rounding_method='HALF-UP')
            if float_compare(uom_qty, qty_done, precision_digits=precision_digits) != 0:
                raise UserError(_('The quantity done for the product "%s" doesn\'t respect the rounding precision \
                                  defined on the unit of measure "%s". Please change the quantity done or the \
                                  rounding precision of your unit of measure.') % (ml.product_id.display_name, ml.product_uom_id.name))

            qty_done_float_compared = float_compare(ml.qty_done, 0, precision_rounding=ml.product_uom_id.rounding)
            if qty_done_float_compared > 0:
                if ml.product_id.tracking != 'none':
                    picking_type_id = ml.move_id.picking_type_id
                    if picking_type_id:
                        if picking_type_id.use_create_lots:
                            # If a picking type is linked, we may have to create a production lot on
                            # the fly before assigning it to the move line if the user checked both
                            # `use_create_lots` and `use_existing_lots`.
                            if ml.lot_name:
                                if ml.product_id.tracking == 'lot' and not ml.lot_id:
                                    lot = self.env['stock.production.lot'].search([
                                        # ('company_id', '=', ml.company_id.id),
                                        ('product_id', '=', ml.product_id.id),
                                        # ('picking_id', '=', ml.picking_id.id),
                                        ('name', '=', ml.lot_name),
                                    ], limit=1)
                                    if lot:
                                        ml.lot_id = lot.id
                                    else:
                                        if ml.picking_id.picking_type_code == 'incoming':
                                            ml._create_and_assign_production_lot()
                                        else:
                                            ml_ids_to_create_lot.add(ml.id)
                                else:
                                    ml_ids_to_create_lot.add(ml.id)
                        elif not picking_type_id.use_create_lots and not picking_type_id.use_existing_lots:
                            # If the user disabled both `use_create_lots` and `use_existing_lots`
                            # checkboxes on the picking type, he's allowed to enter tracked
                            # products without a `lot_id`.
                            continue
                    elif ml.move_id.inventory_id:
                        # If an inventory adjustment is linked, the user is allowed to enter
                        # tracked products without a `lot_id`.
                        continue

                    if not ml.lot_id and ml.id not in ml_ids_to_create_lot:
                        ml_ids_tracked_without_lot.add(ml.id)
            elif qty_done_float_compared < 0:
                raise UserError(_('No negative quantities allowed'))
            else:
                ml_ids_to_delete.add(ml.id)

        if ml_ids_tracked_without_lot:
            mls_tracked_without_lot = self.env['stock.move.line'].browse(ml_ids_tracked_without_lot)
            raise UserError(_('You need to supply a Lot/Serial Number for product: \n - ') +
                              '\n - '.join(mls_tracked_without_lot.mapped('product_id.display_name')))

        if self.picking_id.picking_type_code != 'incoming':
            ml_to_create_lot = self.env['stock.move.line'].browse(ml_ids_to_create_lot)
            ml_to_create_lot._create_and_assign_production_lot()

        mls_to_delete = self.env['stock.move.line'].browse(ml_ids_to_delete)
        mls_to_delete.unlink()

        mls_todo = (self - mls_to_delete)
        mls_todo._check_company()

        # Now, we can actually move the quant.
        ml_ids_to_ignore = OrderedSet()
        for ml in mls_todo:
            if ml.product_id.type == 'product':
                rounding = ml.product_uom_id.rounding

                # if this move line is force assigned, unreserve elsewhere if needed
                if not ml._should_bypass_reservation(ml.location_id) and float_compare(ml.qty_done, ml.product_uom_qty, precision_rounding=rounding) > 0:
                    qty_done_product_uom = ml.product_uom_id._compute_quantity(ml.qty_done, ml.product_id.uom_id, rounding_method='HALF-UP')
                    extra_qty = qty_done_product_uom - ml.product_qty
                    ml_to_ignore = self.env['stock.move.line'].browse(ml_ids_to_ignore)
                    ml._free_reservation(ml.product_id, ml.location_id, extra_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, ml_to_ignore=ml_to_ignore)
                # unreserve what's been reserved
                if not ml._should_bypass_reservation(ml.location_id) and ml.product_id.type == 'product' and ml.product_qty:
                    Quant._update_reserved_quantity(ml.product_id, ml.location_id, -ml.product_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)

                # move what's been actually done
                quantity = ml.product_uom_id._compute_quantity(ml.qty_done, ml.move_id.product_id.uom_id, rounding_method='HALF-UP')
                available_qty, in_date = Quant._update_available_quantity(ml.product_id, ml.location_id, -quantity, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                if available_qty < 0 and ml.lot_id:
                    # see if we can compensate the negative quants with some untracked quants
                    untracked_qty = Quant._get_available_quantity(ml.product_id, ml.location_id, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id, strict=True)
                    if untracked_qty:
                        taken_from_untracked_qty = min(untracked_qty, abs(quantity))
                        Quant._update_available_quantity(ml.product_id, ml.location_id, -taken_from_untracked_qty, lot_id=False, package_id=ml.package_id, owner_id=ml.owner_id)
                        Quant._update_available_quantity(ml.product_id, ml.location_id, taken_from_untracked_qty, lot_id=ml.lot_id, package_id=ml.package_id, owner_id=ml.owner_id)
                Quant._update_available_quantity(ml.product_id, ml.location_dest_id, quantity, lot_id=ml.lot_id, package_id=ml.result_package_id, owner_id=ml.owner_id, in_date=in_date)
            ml_ids_to_ignore.add(ml.id)
        # Reset the reserved quantity as we just moved it to the destination location.
        mls_todo.with_context(bypass_reservation_update=True).write({
            'product_uom_qty': 0.00,
            'date': fields.Datetime.now(),
        })

    