# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TransactionType(models.Model):
	_name = 'transaction.type'
	_description = 'Transaction Type dari Oracle'

	name = fields.Char(string='Transaction Type',)
	description = fields.Char(string='Description',)

	def grab_transaction_type(self):
		for transaction in self:
			# Define connection from Oracle
			con = self.env.company.get_external_connection()
			cur = con.cursor()

			cur.execute("select * from APPS.RA_CUST_TRX_TYPES_ALL_V")

			def makeDictFactory(cur):
				columnNames = [d[0] for d in cur.description]
				def createRow(*args):
					return dict(zip(columnNames, args))
				return createRow

			cur.rowfactory = makeDictFactory(cur)
			result = cur.fetchall()
			for rec in result:
				created_terms = transaction.create({
					'name' : rec['NAME'],
					'description' : rec['DESCRIPTION'],
					})
	

class AccountPaymentTerms(models.Model):
	_inherit = 'account.payment.term'

	def grab_payment_terms(self):
		for terms in self:
			# Define connection from Oracle
			con = self.env.company.get_external_connection()
			cur = con.cursor()

			cur.execute("select * from APPS.RA_TERMS")

			def makeDictFactory(cur):
				columnNames = [d[0] for d in cur.description]
				def createRow(*args):
					return dict(zip(columnNames, args))
				return createRow

			cur.rowfactory = makeDictFactory(cur)
			result = cur.fetchall()
			for rec in result:
				created_terms = terms.create({
					'name' : rec['NAME'],
					'note' : rec['DESCRIPTION'],
					})

