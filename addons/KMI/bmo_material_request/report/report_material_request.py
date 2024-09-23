import json

from odoo import api, models, _
from odoo.tools import float_round

class ReportSoKAI(models.AbstractModel):
    _name = 'report.bmo_material_request.report_material_request'
    _description = 'Report Material Request'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        datas = []
        # lantai_dict = {}
        for rec in docids:
            mr = self.env['material.purchase.requisition'].browse(rec)
            batch_id = mr.batch_production_id
            datas.append({
                'company'       : self.env.user.company_id.name,
                'mr'            : mr,
                'batch_id'      : batch_id,
                'picking'       : mr.delivery_picking_id,
            })
        return {'datas': datas}