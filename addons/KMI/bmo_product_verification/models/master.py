# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class BottleType(models.Model):
	_name = 'bottle.type'
	_description = 'Type of Bottle'

	name = fields.Char(string='Name',)

class FaktorKoreksi(models.Model):
	_name = 'faktor.koreksi'

	name = fields.Char(string='Name',)
	product_id = fields.Many2one('product.product',string='Product',)
	bottle_id = fields.Many2one('bottle.type',string='Type of Bottle',)
	koreksi = fields.Float(string='Faktor Koreksi',)

	@api.constrains('product_id', 'bottle_id')
	def constrains_product_bottle_uniq(self):
		for rec in self:
			if rec.product_id and rec.bottle_id:
				koreksi = rec.search([('product_id','=', rec.product_id.id), ('bottle_id', '=', rec.bottle_id.id),('id', '!=', rec.id) ])
				if koreksi:
					raise ValidationError(_('Product dan Tipe Botol Tidak Boleh Sama.'))




class FaktorWarna(models.Model):
	_name = 'faktor.warna'
	_description = 'Faktor Warna'

	name = fields.Char(string='Name',)
	target = fields.Char(string='Volume Target',)
	yellow = fields.Char(string='Yellow',)
	blue = fields.Char(string='Blue',)
	out_range = fields.Char(string='Out Range',)

	# @api.onchange('target')
	# def _onchange_target(self):
	# 	for rec in self:
	# 		split = rec.target.split('-')
	# 		if len(split) == 1:
	# 			raise ValidationError(_("Masukan 2 nilai target dengan simbol (-) sebagai pemisah"))

	# @api.onchange('out_range')
	# def _onchange_out_range(self):
	# 	for rec in self:
	# 		split = rec.out_range.split('-')
	# 		if len(split) == 1:
	# 			raise ValidationError(_("Masukan 2 nilai target dengan simbol (-) sebagai pemisah"))

	# @api.constrains('target','yellow','blue')
	# def _constrains_parameter(self):
	# 	for rec in self:
	# 		if '-' rec.target 