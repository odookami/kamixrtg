# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime


class StockCardView(models.TransientModel):
    _name = "stock.card.view"
    _description = "Stock Card View"
    _order = "date"

    date = fields.Datetime()
    product_id = fields.Many2one(comodel_name="product.product")
    lot_name = fields.Char("LOT Number")
    expiration_date_char = fields.Char("Expired Date")
    product_qty = fields.Float()
    product_uom_qty = fields.Float()
    product_uom = fields.Many2one(comodel_name="uom.uom")
    reference = fields.Char()
    location_id = fields.Many2one(comodel_name="stock.location")
    location_dest_id = fields.Many2one(comodel_name="stock.location")
    is_initial = fields.Boolean()
    product_in = fields.Float()
    product_out = fields.Float()
    picking_id = fields.Many2one(comodel_name="stock.picking")
    move_line_id = fields.Many2one(comodel_name="Stock.move.line")

    def name_get(self):
        result = []
        for rec in self:
            name = rec.reference
            if rec.picking_id.origin:
                name = "{} ({})".format(name, rec.picking_id.origin)
            result.append((rec.id, name))
        return result


class StockCardReport(models.TransientModel):
    _name = "report.stock.card.report"
    _description = "Stock Card Report"

    # Filters fields, used for data computation
    date_from = fields.Date()
    date_to = fields.Date()
    product_ids = fields.Many2many(comodel_name="product.product")
    location_id = fields.Many2one(comodel_name="stock.location")
    lot_ids = fields.Many2many(
        "stock.production.lot", string="Lot")

    # Data fields, used to browse report data
    results = fields.Many2many(
        comodel_name="stock.card.view",
        compute="_compute_results",
        help="Use compute fields, so there is nothing store in database",
    )
    def revisi_result_sql(self, result):
        data_revisi_qty = []
        list_data = []
        for x in result:
            if x['is_initial'] == True:
                product_id = x['product_id']
                prod_rev = self.env['revisi.onhand'].sudo().search([('product_id','=',product_id)], limit=1)
                if x['date'] <= datetime.strptime('2022-05-01 17:00:00', '%Y-%m-%d %H:%M:%S'):
                    if prod_rev.id not in data_revisi_qty:
                        data_revisi_qty.append(prod_rev.id)
                        list_data.append(
                            {
                                'date': x['date'],
                                'product_id': product_id,
                                'product_qty': prod_rev.qty,
                                'product_uom_qty': prod_rev.qty,
                                'product_uom': prod_rev.product_uom_id,
                                'reference': '', 
                                'location_id': x['location_id'],
                                'location_dest_id': x['location_dest_id'],
                                'product_in': 0,
                                'product_out': 0,
                                'is_initial': x['is_initial'],
                                'picking_id': False,
                                'move_line_id': False,
                                'expiration_date_char': x['expiration_date_char'],
                                'lot_name': x['lot_name'],
                            })
                    else:
                        list_data.append(
                            {
                                'date': x['date'],
                                'product_id': x['product_id'],
                                'product_qty': 0,
                                'product_uom_qty': 0,
                                'product_uom': x['product_uom'],
                                'reference': '', 
                                'location_id': x['location_id'],
                                'location_dest_id': x['location_dest_id'],
                                'product_in': 0,
                                'product_out': 0,
                                'is_initial': x['is_initial'],
                                'picking_id': False,
                                'move_line_id': False,
                                'expiration_date_char': '',
                                'lot_name': ''
                            })
            else:
                list_data.append(x)
        return list_data

    def _compute_results(self):
        self.ensure_one()
        date_from = self.date_from or "0001-01-01"
        self.date_to = self.date_to or fields.Date.context_today(self)
        locations = self.env["stock.location"].search(
            [("id", "child_of", [self.location_id.id])]
        )
        self._cr.execute(
            """
            SELECT 
                move.date, 
                move.product_id,
                move_line.qty_done as product_qty,
                move.product_uom_qty, 
                move_line.product_uom_id as product_uom, 
                move.reference,
                move.location_id, 
                move.location_dest_id,
                case when move_line.location_dest_id in %s
                    then move_line.qty_done end as product_in,
                case when move_line.location_id in %s
                    then move_line.qty_done end as product_out,
                case when move.date < %s then True else False end as is_initial,
                move.picking_id,
                move_line.id as move_line_id
            FROM stock_move move
                JOIN stock_move_line as move_line ON move.id = move_line.move_id
            WHERE (move_line.location_id in %s or move.location_dest_id in %s)
                and move_line.state = 'done' and move.product_id in %s
                and CAST(move.date AS date) <= %s and move_line.check_sc = True
            ORDER BY move.date, move.reference, move_line.id
        """,
            ( 
                tuple(locations.ids),
                tuple(locations.ids),
                date_from,
                tuple(locations.ids),
                tuple(locations.ids),
                tuple(self.product_ids.ids),
                self.date_to,
            ),
        )
        stock_card_results = self._cr.dictfetchall()
        for x in stock_card_results:
            picking_src = self.env['stock.picking'].browse([(x['picking_id'])])
            sml_src = self.env['stock.move.line'].browse([(x['move_line_id'])])
            x['expiration_date_char'] = ''
            if sml_src.lot_id:
                x['lot_name'] = sml_src.lot_id.name
            else:
                x['lot_name'] = sml_src.lot_name
            if sml_src.expiration_date:
                 x['expiration_date_char'] = datetime.strptime(str(sml_src.expiration_date), '%Y-%m-%d %H:%M:%S') or ""
            if sml_src.expired_date:
                 x['expiration_date_char'] = datetime.strptime(str(sml_src.expired_date), '%Y-%m-%d %H:%M:%S') or ""
            if sml_src.product_id.uom_id.id != sml_src.product_uom_id.id:
                x['product_in'] = sml_src.product_uom_id._compute_quantity(x['product_in'], sml_src.product_id.uom_id)
                x['product_out'] = sml_src.product_uom_id._compute_quantity(x['product_out'], sml_src.product_id.uom_id)
                x['product_qty'] = sml_src.product_uom_id._compute_quantity(x['product_qty'], sml_src.product_id.uom_id)
        ReportLine = self.env["stock.card.view"]
        data_lot = []
        for x in self.lot_ids:
            data_lot.append(x.name)
        new_result = self.revisi_result_sql(stock_card_results)
        self.results = [ReportLine.new(
            line).id for line in new_result if line['lot_name'] in tuple(data_lot)]
    

    def _get_initial(self, product_line):
        product_input_qty = sum(product_line.mapped("product_in"))
        product_output_qty = sum(product_line.mapped("product_out"))
        return product_input_qty - product_output_qty

    def print_report(self, report_type="qweb"):
        self.ensure_one()
        action = (
            report_type == "xlsx"
            and self.env.ref("stock_card_report.action_stock_card_report_xlsx")
            or self.env.ref("stock_card_report.action_stock_card_report_pdf")
        )
        return action.report_action(self, config=False)

    def _get_html(self):
        result = {}
        rcontext = {}
        report = self.browse(self._context.get("active_id"))
        if report:
            rcontext["o"] = report
            result["html"] = self.env.ref(
                "stock_card_report.report_stock_card_report_html"
            )._render(rcontext)
        return result

    @api.model
    def get_html(self, given_context=None):
        return self.with_context(given_context)._get_html()
