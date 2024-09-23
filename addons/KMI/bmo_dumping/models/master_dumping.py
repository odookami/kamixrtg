from odoo import models, fields, api


class kmi_dumping(models.Model):
    _name = 'master.dumping'
    _order = 'number asc'
    
    number = fields.Selection(
        [('1.1','1.1'),
         ('2.1','2.1'),('2.2','2.2'),('2.3','2.3'),('2.4','2.4'),('2.5','2.5'),('2.6','2.6'),('2.7','2.7'),('2.8','2.8'),('2.9','2.9'),('2.11','2.11'),
         ('3.1','3.1'),('3.2','3.2'),('3.3','3.3'),('3.4','3.4'),
         ('4.1','4.1'),
         ('5.1','5.1'),],string='The place')
    sequence_ref = fields.Char('No')
    name = fields.Char('Name')
    unit = fields.Char(string='Unit')
    std = fields.Char(string='STD')
    product_id = fields.Many2one(
        "product.product", string="Product")