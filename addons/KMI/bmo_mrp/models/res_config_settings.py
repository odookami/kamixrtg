from odoo import api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'

    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location')
    sampling_location_id = fields.Many2one(
        'stock.location', 'Sampling Location')
    sampling_marketing_location_id = fields.Many2one(
        'stock.location', 'Sampling Marketing Location')
    user_manager_id = fields.Many2one(
        'res.users', 'User Manager')
    reject_fg_location_id = fields.Many2one(
        'stock.location', 'Reject FG Location')

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    scrap_location_id = fields.Many2one(
        'stock.location', 'Scrap Location', related="company_id.scrap_location_id", readonly=False)
    sampling_location_id = fields.Many2one(
        'stock.location', 'Sampling Location', related="company_id.sampling_location_id", readonly=False)
    sampling_marketing_location_id = fields.Many2one(
        'stock.location', 'Sampling Marketing Location', related="company_id.sampling_marketing_location_id", readonly=False)
    
    user_manager_id = fields.Many2one(
        'res.users', 'User Manager', related="company_id.user_manager_id", readonly=False)
    reject_fg_location_id = fields.Many2one(
        'stock.location', 'Reject FG Location', related="company_id.reject_fg_location_id", readonly=False)