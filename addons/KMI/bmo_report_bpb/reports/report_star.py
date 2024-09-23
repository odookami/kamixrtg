# import json

# from odoo import api, models, _
# from odoo.tools import float_round

# class ReportStar(models.Model):
#     _inherit = 'stock.picking'
#     _description = 'Report Star'
    
#     @api.model
#     def action_print_star(self):
#         return self.env.ref('stock.model_stock_picking.action_report_star').report_action(self)