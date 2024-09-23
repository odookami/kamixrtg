# -*- encoding: utf-8 -*-
##############################################################################
#
# Cron QuoTech
# Copyright (C) 2021 (https://cronquotech.odoo.com)
# 
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CqtClearData(models.TransientModel):
    
    _name = 'cqt.clear.data'
    _description = 'Clear Data'

    name = fields.Char('Name',default='Clear Data')
    all_data = fields.Boolean('All Data')
    customer_vendor = fields.Boolean('Customers & Vendors')
    delivery_shipment = fields.Boolean('Transfers')
    sale_delivery = fields.Boolean("Sales & Deliveries")
    purchase_shipment = fields.Boolean('Purchase & Shipments')
    journals = fields.Boolean('Journal Entries')
    invoice_payment_journal = fields.Boolean('Invoices & Payments & Journal Entries')
    chart_of_account = fields.Boolean('Chart Of Accounts & All Accounting Data')

    def return_object(self,objects):
        if objects:
            for obj in objects:
                self.check_and_delete(obj)

    def check_and_delete(self,table):
        sql = """SELECT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND   table_name = '%s');""" % table
        self._cr.execute(sql)
        res = self._cr.dictfetchall()
        res = res and res[0] or {}
        if res.get('exists') == True:
            self.delete_records(table)
        else:
            raise ValidationError(_('No records found!'))

    def delete_records(self,table):
        sql = """DELETE from %s ;""" % table
        self._cr.execute(sql)

    def _clear_sale_delivery(self):
        objects = ['stock_quant','stock_move_line','stock_move',
                    'stock_picking','account_partial_reconcile','account_move_line',
                    'account_move','sale_order_line','sale_order']
        self.return_object(objects)

    def _clear_purchase_shipment(self):
        objects = ['stock_quant','stock_move_line','stock_move',
                    'stock_picking','account_partial_reconcile','account_move_line',
                    'account_move','purchase_order_line','purchase_order']
        self.return_object(objects)

    def _clear_transfer(self):
        objects = ['stock_quant','stock_move_line','stock_move','stock_picking']
        self.return_object(objects)

    def _clear_invoice_payment_journal(self):
        objects = ['account_partial_reconcile','account_move_line','account_move','account_payment']
        self.return_object(objects)

    def _clear_customer_vendor(self):
        query = "DELETE FROM res_partner WHERE id not IN (SELECT partner_id FROM res_users UNION SELECT " \
             "partner_id from res_company); "
        self._cr.execute(query)

    def _clear_chart_of_account(self):
        objects = ['account_move_line','account_move','account_payment',
                    'account_tax','account_bank_statement_line','account_bank_statement','account_payment_register',
                    'account_journal','account_account']
        self.return_object(objects)

    def _clear_journal(self):
        objects = ['account_move_line','account_move']
        self.return_object(objects)
        
    @api.onchange('all_data')
    def onchange_all_data(self):
        if self.all_data:
            self.customer_vendor = True
            self.delivery_shipment = True
            self.sale_delivery = True
            self.purchase_shipment = True
            self.journals = True
            self.invoice_payment_journal = True
            self.chart_of_account = True
        else:
            self.customer_vendor = False
            self.delivery_shipment = False
            self.sale_delivery = False
            self.purchase_shipment = False
            self.journals = False
            self.invoice_payment_journal = False
            self.chart_of_account = False

    def clear_data(self):
        if self.all_data:
            self._clear_sale_delivery()
            self._clear_purchase_shipment()
            self._clear_transfer()
            self._clear_invoice_payment_journal()
            self._clear_customer_vendor()
            self._clear_chart_of_account()
            self._clear_journal()
        if self.sale_delivery:
            self._clear_sale_delivery()
        if self.purchase_shipment:
            self._clear_purchase_shipment()
        if self.delivery_shipment:
            self._clear_transfer()
        if self.invoice_payment_journal:
            self._clear_invoice_payment_journal()
        if self.journals:
            self._clear_journal()
        if self.customer_vendor:
            self._clear_customer_vendor()
        if self.chart_of_account:
            self._clear_chart_of_account()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: