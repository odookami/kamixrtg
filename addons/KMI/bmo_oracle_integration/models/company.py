# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
import cx_Oracle
import os
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ResCompany(models.Model):
	_inherit = 'res.company'

	user_oracle = fields.Char('Oracle Database User')
	pass_oracle = fields.Char('Oracle Database Password')
	ip_oracle = fields.Char('Oracle Database IP')
	port_oracle = fields.Char('Oracle Database Port')
	service_oracle = fields.Char('Oracle Service Name')

	def makeDictFactory(self, cur):
		columnNames = [d[0] for d in cur.description]
		def createRow(*args):
			return dict(zip(columnNames, args))
		return createRow

	def get_external_connection(self):
		user = self.user_oracle
		pw = self.pass_oracle
		dsn = "{}".format(self.ip_oracle+":"+self.port_oracle+"/"+self.service_oracle) 
		try:
			con = cx_Oracle.connect(user, pw, dsn)
			return con
		except Exception as e:
			raise ValidationError(_("Process Terminate : {}".format(e)))


	def test_connection(self):
		user = self.user_oracle
		pw = self.pass_oracle
		dsn = "{}".format(self.ip_oracle+":"+self.port_oracle+"/"+self.service_oracle) #"10.201.10.35:1572/kbndev1"
		# con = cx_Oracle.connect('{}', '{}', "{}".format()) 

		try:
			con = cx_Oracle.connect(user, pw, dsn)
			title = _("Database Connection Online!")
			message = _("Database version: {}".format(con.version) )
			
			return {
				'type': 'ir.actions.client',
				'tag': 'display_notification',
				'params': {
					'title': title,
					'message': message,
					'sticky': False,
				}
			}
		except Exception as e:
			raise ValidationError(_("Process Terminate : {}".format(e)))