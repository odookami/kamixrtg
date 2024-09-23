from odoo import fields, models, api, _
from odoo.addons.bmo_mrp.models.product import state_tipe
from odoo.exceptions import Warning, UserError

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    location_id = fields.Many2one(
        'stock.location', string='Source Location')
    dest_location_id = fields.Many2one(
        'stock.location', string='Destination Location')
    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Picking Type')
    users_ids = fields.Many2many(
        "res.users", string="User Notif")
    product_amf_id = fields.Many2one(
        "product.product", string="Product AMF")
    product_product_id = fields.Many2one('product.product', string="Products Benecol")
    
    product_amf_ids = fields.Many2many(
        "product.product", 'product_amf_ids_rel', string="Product AMF")
    product_product_ids = fields.Many2many('product.product', 'product_product_ids_rel', string="Products Benecol")
        
class AccountReportConfigSettings(models.TransientModel):
    _name = 'material.settings'
    _description = "Material Request Settings"
    _inherit = 'res.config.settings'
    
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    location_id = fields.Many2one(
        'stock.location', string='Source Location', related="company_id.location_id", readonly=False)
    dest_location_id = fields.Many2one(
        'stock.location', string='Destination Location', related="company_id.dest_location_id", readonly=False)
    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Picking Type', related="company_id.picking_type_id", readonly=False)
    users_ids = fields.Many2many(
        "res.users", string="User Notif", related="company_id.users_ids", readonly=False)

    product_amf_ids = fields.Many2many(
        "product.product", 'product_amf_ids_rel', string="Product AMF", related="company_id.product_amf_ids", readonly=False)
    product_product_ids = fields.Many2many('product.product', 'product_product_ids_rel', string="Products Benecol", related="company_id.product_product_ids",readonly=False)

    product_amf_id = fields.Many2one(
        "product.product", string="Product AMF", related="company_id.product_amf_id", readonly=False)
    product_product_id = fields.Many2one('product.product', string="Products Benecol", related="company_id.product_product_id",readonly=False)

class Master_Config_Special_Product(models.Model):
    _name = "config.special.product"

    name = fields.Char("Name")
    product_ids = fields.Many2many(
        "product.product", string="Product")
    config_line = fields.One2many(
        'master.default.location', 'config_id', string='Config Special Line', copy=True,)

class MasterDefaultLocation(models.Model):
    _name = "master.default.location"
    _order = 'tipe desc'


    tipe = fields.Selection(
        state_tipe, string='Type OKP')
    location_id = fields.Many2one(
        'stock.location', string='Source Location')
    dest_location_id = fields.Many2one(
        'stock.location', string='Destination Location')
    dest_location_2_id = fields.Many2one(
        'stock.location', string='Destination Location 2')
    picking_type_2_id = fields.Many2one(
        'stock.picking.type', string='Picking Type 2')
    picking_type_id = fields.Many2one(
        'stock.picking.type', string='Picking Type')
    config_id = fields.Many2one(
        'config.special.product', string='Special Product', ondelete='cascade')
    sequence_ref = fields.Integer(
        'No.', compute="_sequence_ref")
    @api.depends('config_id.config_line', 'config_id.config_line.location_id')
    def _sequence_ref(self):
        for line in self:
            no = 0
            for l in line.config_id.config_line:
                no += 1
                if no >= 4:
                    raise UserError(_("Line Tidak Boleh Lebih Dari 3"))
                l.sequence_ref = no