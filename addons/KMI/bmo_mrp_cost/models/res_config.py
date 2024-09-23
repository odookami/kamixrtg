from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'
    
    product_rm_ids = fields.Many2many(
        "product.product", 'product_product_rm_tag', string="RM")
    product_dl_ids = fields.Many2many(
        "product.product", 'product_product_dl_tag', string="DL")
    product_depre_ids = fields.Many2many(
        "product.product", 'product_product_depre_tag', string="DEPRE")
    product_foh_ids = fields.Many2many(
        "product.product", 'product_product_foh_tag', string="FOH")

class MRPCostSettings(models.TransientModel):
    _name = 'mrp.cost.settings'
    _description = "MRP Cost Settings"
    _inherit = 'res.config.settings'

    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.user.company_id
    )
    product_rm_ids = fields.Many2many(
        "product.product", 'product_product_rm_tag', string="RM", related="company_id.product_rm_ids", readonly=False)
    product_dl_ids = fields.Many2many(
        "product.product", 'product_product_dl_tag', string="DL", related="company_id.product_dl_ids", readonly=False)
    product_depre_ids = fields.Many2many(
        "product.product", 'product_product_depre_tag', string="DEPRE", related="company_id.product_depre_ids", readonly=False)
    product_foh_ids = fields.Many2many(
        "product.product", 'product_product_foh_tag', string="FOH", related="company_id.product_foh_ids", readonly=False)