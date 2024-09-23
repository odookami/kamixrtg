# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    date_report_lhp = fields.Date("Date LHP")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # * BHP
    bhp_location_dest_id = fields.Many2one('stock.location', 
        string='BHP Destination Location')
    bhp_cb_uom_id = fields.Many2one('uom.uom', string='Unit of Measure (CB)')
    bhp_pcs_uom_id = fields.Many2one('uom.uom', string='Unit of Measure (Pcs)')
    date_report_lhp = fields.Date(string="Date LHP", related="company_id.date_report_lhp", readonly=False)

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].sudo().set_param
        set_param('bmo_mrp_packing.bhp_location_dest_id', int(self.bhp_location_dest_id))
        set_param('bmo_mrp_packing.bhp_cb_uom_id', int(self.bhp_cb_uom_id))
        set_param('bmo_mrp_packing.bhp_pcs_uom_id', int(self.bhp_pcs_uom_id))

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param
        res['bhp_location_dest_id'] = int(get_param('bmo_mrp_packing.bhp_location_dest_id'))
        res['bhp_cb_uom_id'] = int(get_param('bmo_mrp_packing.bhp_cb_uom_id'))
        res['bhp_pcs_uom_id'] = int(get_param('bmo_mrp_packing.bhp_pcs_uom_id'))
        return res
    