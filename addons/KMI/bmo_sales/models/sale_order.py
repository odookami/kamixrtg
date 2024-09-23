from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo.tools.float_utils import float_repr
from odoo.tools.misc import format_date
from odoo.exceptions import UserError, ValidationError

class Sale(models.Model):
	_inherit = 'sale.order'

	amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', tracking=False)
	amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=False)
	sales_type = fields.Selection([
		('sales origin', 'Sales Origin' ),('sales sampling','Sales Sampling')
	], string='Sales', default='sales origin')

	# def button_test_convert(self):
	# 	for line in self.order_line:
	# 		qty_convert = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)
	# 		price_convert = line.product_uom._compute_price(line.price_unit, line.product_id.uom_id)
	# 		print(qty_convert)
	# 		print(price_convert)
	def action_confirm(self):
		res = super(Sale, self).action_confirm()
		if self.picking_ids:
			self.picking_ids.action_back_to_draft()
		return res


class SaleOrderLine(models.Model):
	_inherit = "sale.order.line"
	_sql_constraints = [
		('info_po_uniq', 'unique(info_po, order_id)', _('Info PO Harus Unik')),
	]

	info_po = fields.Char('PO Fee')
	qty_pcs = fields.Float(string='Qty (Pcs)',compute='_compute_qty_pcs')

	@api.depends('product_uom', 'product_uom_qty')
	def _compute_qty_pcs(self):
		for line in self:
			line.qty_pcs = line.product_uom._compute_quantity(line.product_uom_qty, line.product_id.uom_id)

	def _prepare_invoice_line(self, **optional_values):
		res = super(SaleOrderLine, self)._prepare_invoice_line()
		for rec in self:
			res['price_unit'] = rec.product_uom._compute_price(rec.price_unit, rec.product_id.uom_id)
			res['quantity'] = rec.product_uom._compute_quantity(rec.product_uom_qty, rec.product_id.uom_id)
			res['product_uom_id'] = rec.product_id.uom_id.id
		return res

	@api.onchange('product_id')
	def product_id_change(self):
		res = super(SaleOrderLine, self).product_id_change()
		self.name = self.product_id.name
		return res


	def _action_launch_stock_rule(self, previous_product_uom_qty=False):
		"""
		Launch procurement group run method with required/custom fields genrated by a
		sale order line. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
		depending on the sale order line product rule.
		"""
		precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
		procurements = []
		for line in self:
			line = line.with_company(line.company_id)
			if line.state != 'sale' or not line.product_id.type in ('consu','product'):
				continue
			qty = line._get_qty_procurement(previous_product_uom_qty)
			if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
				continue

			group_id = line._get_procurement_group()
			if not group_id:
				group_id = self.env['procurement.group'].create(line._prepare_procurement_group_vals())
				line.order_id.procurement_group_id = group_id
			else:
				# In case the procurement group is already created and the order was
				# cancelled, we need to update certain values of the group.
				updated_vals = {}
				if group_id.partner_id != line.order_id.partner_shipping_id:
					updated_vals.update({'partner_id': line.order_id.partner_shipping_id.id})
				if group_id.move_type != line.order_id.picking_policy:
					updated_vals.update({'move_type': line.order_id.picking_policy})
				if updated_vals:
					group_id.write(updated_vals)

			values = line._prepare_procurement_values(group_id=group_id)
			product_qty = line.product_uom_qty - qty

			line_uom = line.product_uom
			quant_uom = line.product_id.uom_id
			# product_qty, procurement_uom = line_uom._adjust_uom_quantities(product_qty, quant_uom)
			# print('ACTION LAUNCH STOCK RULE ########### ', procurement_uom)
			procurements.append(self.env['procurement.group'].Procurement(
				line.product_id, product_qty, line_uom,
				line.order_id.partner_shipping_id.property_stock_customer,
				line.name, line.order_id.name, line.order_id.company_id, values))
		if procurements:
			self.env['procurement.group'].run(procurements)
		return True