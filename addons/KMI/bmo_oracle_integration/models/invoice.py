# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from datetime import timedelta, datetime, date

class AccountMove(models.Model):
	_inherit = 'account.move'

	integration_message = fields.Char('Integration Message')
	oracle_invoice_id = fields.Integer('Oracle Invoice ID')
	transaction_type_id = fields.Many2one('transaction.type',string='Transaction Type',)
	# sequence = fields.Integer('Sequence')
	

	def post_invoice_to_oracle(self):
		invoice_tax_number = ''
		for res in self:
			print('RUNNING POST TO ORACLE ................................................')
			
			query = """
				INSERT INTO APPS.XKAMI_ODOO_SO_DO_STG 
				(STAGING_ID, BATCH_SOURCE_TYPE, TRANSACTION_TYPE, TRANSACTION_DATE, GL_DATE, TERMS_NAME, CUSTOMER_NAME, BILL_TO_CUSTOMER_ID, BILL_TO_ADDRESS_ID, CURRENCY, 
				CONVERSION_TYPE, CONVERSION_DATE, CONVERSION_RATE, ITEMCODE, ITEM_DESCRIPTION, UOM_CODE, QUANTITY, UNIT_PRICE, SALES_ORDER_DATE, SALES_ORDER_LINE_NUM, 
				SHIP_ACTUAL_DATE, PO_CUST_NUMBER, SHIP_CUSTOMER_ID, SHIP_ADDRESS_ID, INTERFACE_LINE_ATTRIBUTE1, INTERFACE_LINE_ATTRIBUTE3, INTERFACE_LINE_ATTRIBUTE6)
				VALUES 
				(:STAGING_ID, :BATCH_SOURCE_TYPE, :TRANSACTION_TYPE, :TRANSACTION_DATE, :GL_DATE, :TERMS_NAME, :CUSTOMER_NAME, :BILL_TO_CUSTOMER_ID, :BILL_TO_ADDRESS_ID, :CURRENCY, 
				:CONVERSION_TYPE, :CONVERSION_DATE, :CONVERSION_RATE, :ITEMCODE, :ITEM_DESCRIPTION, :UOM_CODE, :QUANTITY, :UNIT_PRICE, :SALES_ORDER_DATE, :SALES_ORDER_LINE_NUM, 
				:SHIP_ACTUAL_DATE, :PO_CUST_NUMBER, :SHIP_CUSTOMER_ID, :SHIP_ADDRESS_ID,:INTERFACE_LINE_ATTRIBUTE1, :INTERFACE_LINE_ATTRIBUTE3, :INTERFACE_LINE_ATTRIBUTE6)
			"""
			

			invoice_line_values = [(
				line.move_id.id, 
				'ODOO_INVOICE', 
				'TRADE AFFILIATE', 
				line.move_id.invoice_date, 
				line.move_id.invoice_date, 
				line.move_id.invoice_payment_term_id.name, 
				line.move_id.partner_id.parent_id.name if line.move_id.partner_id.parent_id else line.move_id.partner_id.name, 
				line.move_id.partner_id.cust_account_id, 
				line.move_id.partner_id.cust_acct_site_id, 
				line.move_id.currency_id.name, 
				'User', 
				line.move_id.invoice_date, 
				1, 
				line.product_id.default_code, 
				'TOLL FEE ' + line.product_id.name if line.product_id.name else line.name, 
				line.product_uom_id.name, 
				line.quantity, 
				line.price_unit, 
				line.sale_line_ids[0].order_id.date_order, 
				line.sale_line_ids[0].id, 
				line.sale_line_ids[0].order_id.picking_ids[0].date_done, 
				line.sale_line_ids[0].order_id.client_order_ref if line.sale_line_ids[0].order_id.client_order_ref else '', 
				line.move_id.partner_shipping_id.cust_account_id,
				line.move_id.partner_shipping_id.cust_acct_site_id,
				line.sale_line_ids[0].order_id.name, 
				line.sale_line_ids[0].order_id.picking_ids[0].name, 
				line.id

				) for line in res.invoice_line_ids]

			# for line in invoice_line_values:
			# 	print(line)
			# 	print(len(line))
			# print(len(line) for line in invoice_line_values)
			con = self.env.company.get_external_connection()
			cur = con.cursor()
			cur.prepare(query)
			cur.executemany(None, invoice_line_values)
			con.commit()
			con.close()

	def action_post(self):
		res = super(AccountMove, self).action_post()
		self.post_invoice_to_oracle()
		return res