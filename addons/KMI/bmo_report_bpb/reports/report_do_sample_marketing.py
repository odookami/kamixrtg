from odoo import api, fields, models
from datetime import datetime
import time
import itertools
from dateutil.relativedelta import relativedelta


class ReportDo(models.AbstractModel):
    _name = 'report.bmo_report_bpb.report_do_sample_marketing'
    _description = 'DELIVERY ORDER SAMPLE MARKETING'

    @api.model
    def _get_report_values(self, docids, data=None):
        name = 'bmo_report_bpb.report_do_sample_marketing'
        report = self.env['ir.actions.report']._get_report_from_name(name)
        docs = self.env[report.model].browse(docids)
        result = []
        lot_exist = []
        data_dict = {}
        for doc in docs:
            for rec in doc.move_line_ids:
                if rec.product_id.alias not in data_dict:
                    data_dict[rec.product_id.alias] = {rec.lot_new: [rec]}
                else:
                    if rec.lot_new not in data_dict[rec.product_id.alias]:
                        data_dict[rec.product_id.alias][rec.lot_new] = [rec]
                    else:
                        data_dict[rec.product_id.alias][rec.lot_new].append(rec)
                        
            list_product = []
            no = 1
            for k, v in data_dict.items():
                product = self.env['product.product'].search([('alias', '=', k)], limit=1)
                for u, i in v.items():
                    qty = 0
                    data_list = []
                    exp_new = ''
                    for x in i:
                        qty = x.qty_done
                        if rec.product_uom_id.id != rec.product_id.uom_id.id:
                            qty = rec.product_uom_id._compute_quantity(qty, rec.product_id.uom_id, rounding_method='HALF-UP')
                        exp_new = x.exp_lot.strftime("%d-%b-%Y")
                        data_list.append(qty)
                    product_name = product.alis_name
                    product_code = product.alias
                    number = no
                    if k in list_product:
                        product_name = ''
                        product_code = ''
                        # exp_new = ''
                        number = ''
                        no -= 1
                    result.append({
                        'no'       : number,
                        'product': product_name,
                        'item_code': product_code,
                        'lot': u or '',
                        'exp': exp_new if rec.exp_lot else '',
                        'qty_cb': sum([x.qty_done for x in i]) or 0,
                        'qty_pcs': sum(data_list) or 0,
                    })
                    list_product.append(k)
                    no += 1
        return {
            'result': result,
            'docs': docs,
            'doc_model': report.model,
            'report_type': data.get('report_type') if data else '',
        }
