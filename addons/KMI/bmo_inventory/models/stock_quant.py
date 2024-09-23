import logging

from psycopg2 import Error, OperationalError

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    _order = "expiration_date ASC, location_id ASC, id"

    product_code = fields.Char("Kode Item", related="product_id.default_code")
    product_name = fields.Char("Name Item", related="product_id.name")
    expiration_date = fields.Datetime(string='Expiration Date', related="lot_id.expiration_date",
        help='This is the date on which the goods with this Serial Number may become dangerous and must not be consumed.', store=True)
    quantity = fields.Float(
        'Quantity', digits='Product Unit of Measure',
        help='Quantity of products in this quant, in the default unit of measure of the product',
        readonly=True)
    inventory_quantity = fields.Float(
        'Inventoried Quantity', compute='_compute_inventory_quantity', digits='Product Unit of Measure',
        inverse='_set_inventory_quantity', groups='stock.group_stock_manager')
    reserved_quantity = fields.Float(
        'Reserved Quantity',
        default=0.0, digits='Product Unit of Measure',
        help='Quantity of reserved products in this quant, in the default unit of measure of the product',
        readonly=True, required=True)
    available_quantity = fields.Float(
        'Available Quantity', digits='Product Unit of Measure',
        help="On hand quantity which hasn't been reserved on a transfer, in the default unit of measure of the product",
        compute='_compute_available_quantity')

    @api.model
    def _get_removal_strategy_order(self, removal_strategy):
        if removal_strategy == 'fefo':
            return 'expiration_date, location_id, in_date, id'
        return super(StockQuant, self)._get_removal_strategy_order(removal_strategy)
        
    def _gather_by_id(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, quant_id=None):
        self.env['stock.quant'].flush(['location_id', 'owner_id', 'package_id', 'lot_id', 'product_id'])
        self.env['product.product'].flush(['virtual_available'])
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        removal_strategy_order = self._get_removal_strategy_order(removal_strategy)
        domain = [
            ('product_id', '=', product_id.id),
        ]
        if not strict:
            if quant_id:
                domain = expression.AND([[('id', '=', quant_id.id)], domain])
            if lot_id:
                domain = expression.AND([[('lot_id', '=', lot_id.id)], domain])
            if package_id:
                domain = expression.AND([[('package_id', '=', package_id.id)], domain])
            if owner_id:
                domain = expression.AND([[('owner_id', '=', owner_id.id)], domain])
            domain = expression.AND([[('location_id', 'child_of', location_id.id)], domain])
        else:
            domain = expression.AND([[('id', '=', quant_id and quant_id.id or False)], domain])
            domain = expression.AND([[('lot_id', '=', lot_id and lot_id.id or False)], domain])
            domain = expression.AND([[('package_id', '=', package_id and package_id.id or False)], domain])
            domain = expression.AND([[('owner_id', '=', owner_id and owner_id.id or False)], domain])
            domain = expression.AND([[('location_id', '=', location_id.id)], domain])

        # Copy code of _search for special NULLS FIRST/LAST order
        self.check_access_rights('read')
        query = self._where_calc(domain)
        self._apply_ir_rules(query, 'read')
        from_clause, where_clause, where_clause_params = query.get_sql()
        where_str = where_clause and (" WHERE %s" % where_clause) or ''
        query_str = 'SELECT "%s".id FROM ' % self._table + from_clause + where_str + " ORDER BY "+ removal_strategy_order
        self._cr.execute(query_str, where_clause_params)
        res = self._cr.fetchall()
        # No uniquify list necessary as auto_join is not applied anyways...
        return self.browse([x[0] for x in res])
    
    @api.model
    def _update_reserved_quantity_by_id(self, product_id, location_id, quantity, lot_id=None, package_id=None, owner_id=None, strict=False, quant_id=None):
        self = self.sudo()
        rounding = product_id.uom_id.rounding
        quants = self._gather_by_id(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict, quant_id=quant_id)
        reserved_quants = []

        if float_compare(quantity, 0, precision_rounding=rounding) > 0:
            # if we want to reserve
            available_quantity = self._get_available_quantity(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
            if float_compare(quantity, available_quantity, precision_rounding=rounding) > 0:
                raise UserError(_('It is not possible to reserve more products of %s than you have in stock.', product_id.display_name))
        elif float_compare(quantity, 0, precision_rounding=rounding) < 0:
            # if we want to unreserve
            available_quantity = sum(quants.mapped('reserved_quantity'))
            if float_compare(abs(quantity), available_quantity, precision_rounding=rounding) > 0:
                raise UserError(_('It is not possible to unreserve more products of %s than you have in stock.', product_id.display_name))
        else:
            return reserved_quants

        for quant in quants:
            if float_compare(quantity, 0, precision_rounding=rounding) > 0:
                max_quantity_on_quant = quant.quantity - quant.reserved_quantity
                if float_compare(max_quantity_on_quant, 0, precision_rounding=rounding) <= 0:
                    continue
                max_quantity_on_quant = min(max_quantity_on_quant, quantity)
                quant.reserved_quantity += max_quantity_on_quant
                reserved_quants.append((quant, max_quantity_on_quant))
                quantity -= max_quantity_on_quant
                available_quantity -= max_quantity_on_quant
            else:
                max_quantity_on_quant = min(quant.reserved_quantity, abs(quantity))
                quant.reserved_quantity -= max_quantity_on_quant
                reserved_quants.append((quant, -max_quantity_on_quant))
                quantity += max_quantity_on_quant
                available_quantity += max_quantity_on_quant

            if float_is_zero(quantity, precision_rounding=rounding) or float_is_zero(available_quantity, precision_rounding=rounding):
                break
        return reserved_quants
    
    def update_lot_by_quant(self):
        for rec in self:
            lot_id = rec.lot_id
            product_quant = rec.product_id
            if lot_id.product_id.id != product_quant.id:
                lot_new = self.env['stock.production.lot'].create({'name' : lot_id.id, 'product_id' : product_quant.id, 'company_id': rec.company_id.id})
                rec.sudo().write({'lot_id' : lot_new})
    
    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        """ Called when user manually set a new quantity (via `inventory_quantity`)
        just before creating the corresponding stock move.

        :param location_id: `stock.location`
        :param location_dest_id: `stock.location`
        :param out: boolean to set on True when the move go to inventory adjustment location.
        :return: dict with all values needed to create a new `stock.move` with its move line.
        """
        self.ensure_one()
        # return {
        #     'name': _('Product Quantity Updated'),
        #     'product_id': self.product_id.id,
        #     'product_uom': self.product_uom_id.id,
        #     'product_uom_qty': qty,
        #     'company_id': self.company_id.id or self.env.company.id,
        #     'state': 'confirmed',
        #     'location_id': location_id.id,
        #     'location_dest_id': location_dest_id.id,
        #     'move_line_ids': [(0, 0, {
        #         'product_id': self.product_id.id,
        #         'product_uom_id': self.product_uom_id.id,
        #         'qty_done': qty,
        #         'location_id': location_id.id,
        #         'location_dest_id': location_dest_id.id,
        #         'company_id': self.company_id.id or self.env.company.id,
        #         'lot_id': self.lot_id.id,
        #         'package_id': out and self.package_id.id or False,
        #         'result_package_id': (not out) and self.package_id.id or False,
        #         'owner_id': self.owner_id.id,
        #     })]
        # }
        return False

    def name_get(self):
        result = []
        for record in self:
            name = f'[{record.product_id.default_code}] {record.location_id.complete_name} {record.lot_id.name} [{record.available_quantity}]'
            result.append((record.id, name))
        return result



    # CADANGAN KASUS LOT ID QUARANTINE
    # @api.model
    # def _get_available_quantity(self, product_id, location_id, lot_id=None, package_id=None, owner_id=None, strict=False, allow_negative=False):
    # 	""" Return the available quantity, i.e. the sum of `quantity` minus the sum of
    # 	`reserved_quantity`, for the set of quants sharing the combination of `product_id,
    # 	location_id` if `strict` is set to False or sharing the *exact same characteristics*
    # 	otherwise.
    # 	This method is called in the following usecases:
    # 		- when a stock move checks its availability
    # 		- when a stock move actually assign
    # 		- when editing a move line, to check if the new value is forced or not
    # 		- when validating a move line with some forced values and have to potentially unlink an
    # 		  equivalent move line in another picking
    # 	In the two first usecases, `strict` should be set to `False`, as we don't know what exact
    # 	quants we'll reserve, and the characteristics are meaningless in this context.
    # 	In the last ones, `strict` should be set to `True`, as we work on a specific set of
    # 	characteristics.

    # 	:return: available quantity as a float
    # 	"""
    # 	self = self.sudo()
    # 	quants = self._gather(product_id, location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=strict)
    # 	# for q in quants:
    # 	# 	print(q.location_id.name)
    # 	# print(q.location_id.name for q in quants)
    # 	rounding = product_id.uom_id.rounding
    # 	if product_id.tracking == 'none':
    # 		available_quantity = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
    # 		if allow_negative:
    # 			return available_quantity
    # 		else:
    # 			return available_quantity if float_compare(available_quantity, 0.0, precision_rounding=rounding) >= 0.0 else 0.0
    # 	else:
    # 		availaible_quantities = {lot_id: 0.0 for lot_id in list(set(quants.mapped('lot_id'))) + ['untracked']}

    # 		for quant in quants:
    # 			if not quant.lot_id:
    # 				availaible_quantities['untracked'] += quant.quantity - quant.reserved_quantity
    # 			else:
    # 				availaible_quantities[quant.lot_id] += quant.quantity - quant.reserved_quantity
    # 		for k, y in availaible_quantities.items():
    # 			if k != 'untracked':
    # 				# print(k)
    # 				availaible_quantities[k] = y - k.qty_karantina
    # 		if allow_negative:
    # 			return sum(availaible_quantities.values())
    # 		else:
    # 			return sum([available_quantity for available_quantity in availaible_quantities.values() if float_compare(available_quantity, 0, precision_rounding=rounding) > 0])