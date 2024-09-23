# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # * PM Harian - Product Category
    pm_categ_id = fields.Many2one('product.category', string='PM Product Category')

    # * PM Harian - Return to WHS
    return_loc_id = fields.Many2one('stock.location', string='Source Location')
    return_dest_id = fields.Many2one('stock.location', string='Destination Location')
    
    # * PM Harian - Gain
    gain_loc_id = fields.Many2one('stock.location', string='Source Location')
    gain_dest_id = fields.Many2one('stock.location', string='Destination Location')

    # * PM Harian - Loss
    loss_loc_id = fields.Many2one('stock.location', string='Source Location')
    loss_dest_id = fields.Many2one('stock.location', string='Destination Location')
    
    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('bmo_mrp_material.pm_categ_id', int(self.pm_categ_id))
        set_param('bmo_mrp_material.return_loc_id', int(self.return_loc_id))
        set_param('bmo_mrp_material.return_dest_id', int(self.return_dest_id))
        set_param('bmo_mrp_material.gain_loc_id', int(self.gain_loc_id))
        set_param('bmo_mrp_material.gain_dest_id', int(self.gain_dest_id))
        set_param('bmo_mrp_material.loss_loc_id', int(self.loss_loc_id))
        set_param('bmo_mrp_material.loss_dest_id', int(self.loss_dest_id))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['pm_categ_id'] = int(get_param('bmo_mrp_material.pm_categ_id'))
        res['return_loc_id'] = int(get_param('bmo_mrp_material.return_loc_id'))
        res['return_dest_id'] = int(get_param('bmo_mrp_material.return_dest_id'))
        res['gain_loc_id'] = int(get_param('bmo_mrp_material.gain_loc_id'))
        res['gain_dest_id'] = int(get_param('bmo_mrp_material.gain_dest_id'))
        res['loss_loc_id'] = int(get_param('bmo_mrp_material.loss_loc_id'))
        res['loss_dest_id'] = int(get_param('bmo_mrp_material.loss_dest_id'))
        return res
    