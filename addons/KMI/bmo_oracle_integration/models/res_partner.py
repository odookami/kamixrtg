# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
	_inherit = 'res.partner'

	# id_oracle = fields.Integer('ID Oracle')
	cust_account_id = fields.Integer('Cust Account ID')
	cust_acct_site_id = fields.Integer('Cust Acct Site ID')
	party_id = fields.Integer(string='Party ID',)

	def grab_supplier(self, where_condition=False):
		# for partner in self:
			# Define connection from Oracle
		con = self.env.company.get_external_connection()
		cur = con.cursor()

		partner = self
		bank_obj = self.env['res.bank']
		query = "select * from APPS.XKAMI_CUSTOMER_LIST_V"
		if where_condition:
			query += " where CUST_ACCT_SITE_ID not in {}".format(tuple(where_condition))
		print(query)
		cur.execute(query)

		def makeDictFactory(cur):
			columnNames = [d[0] for d in cur.description]
			def createRow(*args):
				return dict(zip(columnNames, args))
			return createRow

		cur.rowfactory = makeDictFactory(cur)
		result = cur.fetchall()
		# result = cur.fetchone()
		# print(result)
		# #try to create supplier
		# # values = {}
		partners = []
		parent_customer = [res for res in result if res['CUST_ACCOUNT_ID'] == res['CUST_ACCT_SITE_ID']]
		child_customer = [res for res in result if res['CUST_ACCOUNT_ID'] != res['CUST_ACCT_SITE_ID']]
		print('----- PARENT ------')
		print(parent_customer)
		# print('----- CHILD ------')
		# print(child_customer)
		for parent in parent_customer:
			address = [parent['ADDRESS2'],parent['ADDRESS3'],parent['ADDRESS4']]
			country_id = self.env['res.country'].search([('code', '=', parent['COUNTRY'])]).id if parent['COUNTRY'] else False
			# state = parent['PROVINCE']
			state_id = self.env['res.country.state'].search([('name', '=', parent['PROVINCE'])]).id if parent['PROVINCE'] else False
			created_partner = partner.create({
				# 'id_oracle' : parent['CUST_ACCOUNT_ID'],
				'party_id' : parent['PARTY_ID'],
				'name' : parent['CUSTOMER_NAME'],
				'cust_account_id' : parent['CUST_ACCOUNT_ID'],
				'cust_acct_site_id' : parent['CUST_ACCT_SITE_ID'],
				'street' : parent['ADDRESS1'],
				'street2' : ' '.join(x for x in address if type(x) == 'str'),
				'city' : parent['CITY'],
				'customer_rank' : 1,
				'zip' : parent['POSTAL_CODE'],
				'state_id' : state_id,
				'country_id' : country_id,
				})
			partners.append(created_partner.id)
			
		for child in child_customer:
			address = [child['ADDRESS2'],child['ADDRESS3'],child['ADDRESS4']]
			country_id = self.env['res.country'].search([('code', '=', child['COUNTRY'])]).id if child['COUNTRY'] else False
			# if not child['CITY']:
			# 	raise ValidationError(_("Kolom City pada oracle harap diisi, dikarenakan sebagai acuan alamat pengiriman. Reference : {}".format(child['CUST_ACCT_SITE_ID'])))
			# state = parent['PROVINCE']
			state_id = self.env['res.country.state'].search([('name', '=', child['PROVINCE'])]).id if child['PROVINCE'] else False
			parent_id = self.search([('cust_acct_site_id', '=', child['CUST_ACCOUNT_ID'])]).id
			# name = [child['CUSTOMER_NAME'] + child['ADDRESS1']]
			created_partner = partner.create({
				'company_type' : 'person' if parent_id else 'company',
				'parent_id' : parent_id,
				'type' : 'invoice' if child['SITE_USE_CODE'] == 'BILL_TO' else 'delivery',
				'party_id' : child['PARTY_ID'],
				'name' : child['ADDRESS1'] if parent_id else child['CUSTOMER_NAME'],
				'cust_account_id' : child['CUST_ACCOUNT_ID'],
				'cust_acct_site_id' : child['CUST_ACCT_SITE_ID'],
				'street' : child['ADDRESS1'],
				'street2' : ' '.join(x for x in address if type(x) == 'str'),
				'city' : child['CITY'],
				'customer_rank' : 1,
				'zip' : child['POSTAL_CODE'],
				'state_id' : state_id,
				'country_id' : country_id,
				})
			partners.append(created_partner.id)

		return partner.browse(partners)
# {
#   "PARTY_ID": 6048,
#   "CUSTOMER_NAME": "MILKO BEVERAGE INDUSTRY, PT",
#   "CUST_ACCOUNT_ID": 2042,
#   "ACCOUNT_NUMBER": "1020",
#   "ORG_ID": 82,
#   "CUST_ACCT_SITE_ID": 1182,
#   "PARTY_SITE_NUMBER": "1060",
#   "SITE_USE_CODE": "BILL_TO",
#   "ADDRESS1": "JL. MAYJEN H.R.E SUKMA KM. 15 NO. 3",
#   "ADDRESS2": "CIHERANG PONDOK",
#   "ADDRESS3": "CARINGIN",
#   "ADDRESS4": null,
#   "CITY": "BOGOR",
#   "POSTAL_CODE": null,
#   "STATE": null,
#   "PROVINCE": "WEST JAVA",
#   "COUNTRY": "ID",
#   "ADDRESS_STYLE": "POSTAL_ADDR_DEF"
# }
			# print(parent_customer)
			


