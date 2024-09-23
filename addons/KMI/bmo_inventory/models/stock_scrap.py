from odoo import models, fields, api, _


class MasterType(models.Model):
    _name = 'master.type'

    name = fields.Char("Name")
    location_id = fields.Many2one(
        'stock.location', 'Sampling Location')

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    state = fields.Selection(selection_add=[('confirmed','Confirmed'),('done', 'Done')])
    master_type_id = fields.Many2one(
        "master.type", string="Type Scrap")
    tipe = fields.Selection(
        [('scrap','Scrap'),('sampling','Sampling'),('sampling_marketing','Sampling Marketing')], string="Type", default="scrap")
    

    @api.onchange('master_type_id')
    def _onchange_master_type_id(self):
        for rec in self:
            if rec.master_type_id:
                rec.scrap_location_id = rec.master_type_id.location_id.id
                
    def action_confirmed(self):
        for rec in self:
            rec.write({'state' : 'confirmed'})