# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class ProductGroup(models.Model):
	_name = 'product.group'
	_description = 'Untuk pengelompokan produk sehingga bisa diimport langsung berdasarkan template yang ada'

	name  = fields.Char(string='Group Name',)
	code = fields.Char(string='Code')
	product_id  = fields.Many2one('product.product',string='Group Product',)
	product_group_line = fields.One2many('product.group.line','product_group_id',string='Products',)
	active = fields.Boolean(string='Active', default=True)

class ProductGroupLine(models.Model):
	_name = 'product.group.line'
	_description = 'Daftar product, qty dan uom'

	product_group_id = fields.Many2one('product.group',string='Product Group',)
	product_id = fields.Many2one('product.product',string='Product',)
	qty = fields.Float(string='Quantity',)
	uom_id = fields.Many2one('uom.uom',string='Unit of Measure',)