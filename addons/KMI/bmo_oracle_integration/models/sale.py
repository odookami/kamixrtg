# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo.exceptions import ValidationError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    transaction_type_id = fields.Many2one('transaction.type',string='Transaction Type',)
    need_integration = fields.Boolean(string='Integration', copy=False)
    sent_oracle = fields.Boolean(string='Sent',copy=False)
    date_delivery = fields.Datetime(compute='_compute_date_delivery_kmi', string='Delivery Date', store=True)
    
    @api.depends('picking_ids','picking_ids.state','picking_ids.date_done')
    def _compute_date_delivery_kmi(self):
        for rec in self:
            for picking in rec.picking_ids:
                rec.date_delivery = picking.date_done or ''

    def _action_confirm(self):
        for rec in self:
            rec.need_integration = True
        return super(SaleOrder, self)._action_confirm()

    # def _compute_need_integration(self):
    # 	for rec in self:

    def check_order_and_delivered(self):
        # for ol in self.order_line:
        # 	if ol.product_uom_qty != ol.product_qty:
        # 		print('ERROR ADA DI SINI')
        if any(ol.product_uom_qty != ol.qty_delivered for ol in self.order_line):
            raise ValidationError(_('Qty Order tidak sama dengan QTY Delivered.'))
            # raise (_())


    def post_invoice_to_oracle(self):
        # self.check_order_and_delivered()
        invoice_tax_number = ''
        if self.sent_oracle:
            raise ValidationError(_("Sales Order sudah pernah dikirim ke Oracle Environment. Mohon untuk membuat Sale Order kembali."))
        for rec in self:
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

            picking_ids = rec.picking_ids.filtered(lambda p:p.state == 'done')

            invoice_line_values = []
            for picking in picking_ids:
                for line in picking.move_ids_without_package:
                    invoice_line_values.append((
                        rec.id, # 1
                        'ODOO_INVOICE', # 2 
                        'TRADE AFFILIATE', # 3
                        rec.date_delivery, # 4
                        rec.date_delivery, # 5
                        rec.payment_term_id.name,  # 6
                        rec.partner_id.parent_id.name if rec.partner_id.parent_id else rec.partner_id.name, # 7
                        rec.partner_id.cust_account_id, # 8
                        rec.partner_id.cust_acct_site_id, # 9
                        rec.currency_id.name, # 10
                        'User', # 11
                        rec.date_order, # 12 
                        1, # 13
                        line.product_id.default_code, # 14
                        'TOLL FEE ' + line.product_id.name if line.product_id.name else line.name, # 15
                        line.product_id.uom_id.name, # 16
                        line.product_uom._compute_quantity(line.quantity_done, line.product_id.uom_id), # 17
                        line.sale_line_id.product_uom._compute_price(line.sale_line_id.price_unit, line.sale_line_id.product_id.uom_id), # 18
                        rec.date_order, # 19
                        line.sale_line_id.id, # 20
                        picking.date_done, # 21
                        line.sale_line_id.info_po if line.sale_line_id.info_po else '' , # 22
                        rec.partner_shipping_id.cust_account_id, # 23
                        rec.partner_shipping_id.cust_acct_site_id, # 24
                        rec.name, # 25
                        picking.name, # 26
                        str(line.id), # 27
                    ))
            print(invoice_line_values)
                        # rec.client_order_ref if rec.client_order_ref else '', # 22
                    
            # for val in invoice_line_values:
            # 	print(val)
            # print(val for val in invoice_line_values)
            # print(len(line) for line in invoice_line_values)
            con = rec.env.company.get_external_connection()
            cur = con.cursor()
            cur.prepare(query)
            cur.executemany(None, invoice_line_values)
            con.commit()
            con.close()
            # jika data sudah masuk ke oracle staging tanpa error, maka nilai need integration menjadi False dan sent_oracle menjadi True
            rec.need_integration = False
            rec.sent_oracle = True


    # def _create_invoices(rec. grouped=False, final=False, date=None):
    # 	res = super(SaleOrder, rec.._create_invoices(grouped, final, date)
    # 	print(res.transaction_type_id)
    # 	res.write({'transaction_type_id' : res.transaction_type_id.id})
    # 	# res.action_post()
    # 	return res


