from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    reject_fg_location_id = fields.Many2one(
        'stock.location', 'Reject FG Location')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    reject_fg_location_id = fields.Many2one(
        'stock.location', 'Reject FG Location', related="company_id.reject_fg_location_id", readonly=False)