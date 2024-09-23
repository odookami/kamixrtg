from odoo import api, fields, models
from datetime import datetime
import time
import itertools
from dateutil.relativedelta import relativedelta


class ReportDo(models.AbstractModel):
    _name = 'report.bmo_report_bpb.report_do'
    _description = 'Report Do'

    @api.model
    def _get_report_values(self, docids, data=None):
        name = 'bmo_report_bpb.report_do'
        report = self.env['ir.actions.report']._get_report_from_name(name)
        docs = self.env[report.model].browse(docids)
        result = []
        lot_exist = []
        data_dict = {}
        list_product = []
        for doc in docs:
            for rec in doc.move_line_ids:
                if rec.product_id.id not in data_dict:
                    data_dict[rec.product_id.id] = {rec.lot_id.name : [rec]}
                else:
                    if rec.lot_id.name not in data_dict[rec.product_id.id]:
                        data_dict[rec.product_id.id][rec.lot_id.name] = [rec]
                    else:
                        data_dict[rec.product_id.id][rec.lot_id.name].append(rec)
        no = 1
        for k, v in data_dict.items():
            product = self.env['product.product'].browse(k)
            for u, i in v.items():
                lot = self.env['stock.production.lot'].search([('name','=', u)],limit=1)
                qty = 0
                data_list = []
                for x in i:
                    qty = x.qty_done
                    if rec.product_uom_id.id != rec.product_id.uom_id:  
                        qty = rec.product_uom_id._compute_quantity(qty, rec.product_id.uom_id, rounding_method='HALF-UP')
                    data_list.append(qty)
                value_ed = lot.expiration_date + relativedelta(hours=7)
                product_name = product.name
                product_code = product.default_code
                number = no
                if k in list_product:
                    product_name = ''
                    product_code = ''
                    number = ''
                    no -= 1
                result.append({
                            'no'        : number,
                            'product'   : product_name,
                            'item_code' : product_code,
                            'lot'       : u or '',
                            'exp'       : value_ed.strftime("%d-%b-%Y") or '',
                            'qty_cb'    : sum([x.qty_done for x in i])  or 0,
                            'qty_pcs'   : sum(data_list) or 0,
                        })   
                list_product.append(k)
                no += 1
        return {
                'result': result,
                'docs': docs,
                'doc_model': report.model,
                'report_type': data.get('report_type') if data else '',
            }
    