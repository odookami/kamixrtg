# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class SaleAdvancePaymentInv(models.TransientModel):
	_inherit = 'sale.advance.payment.inv'

	# @api.model
	# def default_get(self, fields):
	# 	res = super(SaleAdvancePaymentInv, self).default_get(fields)
	# 	print('RESSSSSSSSSSSSS', res)
	# 	return res

	def _prepare_invoice_values(self, order, name, amount, so_line):
		res = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(order, name, amount, so_line)
		res.update({
			'transaction_type_id' : order.transaction_type_id.id,
			})
		return res

	def _create_invoice(self, order, so_line, amount):
		res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
		res.action_post()
		print('RESSSSSSSSS ##################### ', res)
		return res

	def create_invoices(self):
		sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))

		if self.advance_payment_method == 'delivered':
			invoice = sale_orders._create_invoices(final=self.deduct_down_payments)
			invoice.transaction_type_id = sale_orders.transaction_type_id.id
			invoice.invoice_date = sale_orders.date_order
			invoice.action_post()
			print('MASUK KONDISI PERTAMA ? ', invoice.invoice_date)
		else:
			# Create deposit product if necessary
			print('MASUK KONDISI KEDUA ?')
			if not self.product_id:
				vals = self._prepare_deposit_product()
				self.product_id = self.env['product.product'].create(vals)
				self.env['ir.config_parameter'].sudo().set_param('sale.default_deposit_product_id', self.product_id.id)

			sale_line_obj = self.env['sale.order.line']
			for order in sale_orders:
				print('MASUK LOOPINGAN ???')
				amount, name = self._get_advance_details(order)

				if self.product_id.invoice_policy != 'order':
					raise UserError(_('The product used to invoice a down payment should have an invoice policy set to "Ordered quantities". Please update your deposit product to be able to create a deposit invoice.'))
				if self.product_id.type != 'service':
					raise UserError(_("The product used to invoice a down payment should be of type 'Service'. Please use another product or update this product."))
				taxes = self.product_id.taxes_id.filtered(lambda r: not order.company_id or r.company_id == order.company_id)
				tax_ids = order.fiscal_position_id.map_tax(taxes, self.product_id, order.partner_shipping_id).ids
				analytic_tag_ids = []
				for line in order.order_line:
					analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

				so_line_values = self._prepare_so_line(order, analytic_tag_ids, tax_ids, amount)
				so_line = sale_line_obj.create(so_line_values)
				invoice = self._create_invoice(order, so_line, amount)
				invoice.write({'transaction_type_id' : order.transaction_type_id.id})
				invoice.action_post()
		if self._context.get('open_invoices', False):
			return sale_orders.action_view_invoice()
		return {'type': 'ir.actions.act_window_close'}