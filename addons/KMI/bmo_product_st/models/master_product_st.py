from odoo import models, fields, api


class master_product_st(models.Model):
    _name = 'master.product.st'
    _description = 'Master Product ST'
    

    name = fields.Char(
        string='Uraian Kegiatan')
    unit = fields.Char(
        'Unit')
    parameter = fields.Char(
        'Parameter')
    number = fields.Char(
        'No')
    product_id = fields.Many2one(
        "product.product", string="Product")