from odoo import _, api, fields, models


class Users(models.Model):
    _inherit = 'res.users'

    location_id = fields.Many2many(
        'stock.location', 'location_security_stock_location_users', 'user_id', 'location_id', 'Stock Locations')
    picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel', 'user_id', 'picking_type_id', string='Warehouse Operations')
