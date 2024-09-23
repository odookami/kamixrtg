import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

state_tipe = [('Mixing', 'Mixing'), ('Filling', 'Filling'), ('Banded', 'Banded')]

class TypeCategory(models.Model):
    _name = "type.category"
    _description = 'Type Category'

    name = fields.Char("Name")
    code = fields.Char("code")

class ProductTemplate(models.Model):
    _inherit = "product.template"

    tipe = fields.Selection(
        state_tipe, string='Type OKP')
    tipe_category = fields.Many2one(
        'type.category', string='QC FG')

class ProductProduct(models.Model):
    _inherit = "product.product"

    tipe = fields.Selection(state_tipe, string='Type OKP', related="product_tmpl_id.tipe", stroe=True)
    tipe_category = fields.Many2one(
        'type.category', string='QC FG', related="product_tmpl_id.tipe_category", stroe=True)