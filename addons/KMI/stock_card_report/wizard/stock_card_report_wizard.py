# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class StockCardReportWizard(models.TransientModel):
    _name = "stock.card.report.wizard"
    _description = "Stock Card Report Wizard"

    date_range_id = fields.Many2one(comodel_name="date.range", string="Period")
    date_from = fields.Date(string="Start Date")
    date_to = fields.Date(string="End Date")
    location_id = fields.Many2one(
        comodel_name="stock.location", string="Location", required=True
    )
    all_product = fields.Boolean("All Product")
    product_ids = fields.Many2many(
        comodel_name="product.product", string="Products", required=True
    )
    all_lot = fields.Boolean(
        "All Lot", default=True)
    lot_ids = fields.Many2many(
        "stock.production.lot", string="Lot", required=False)

    @api.onchange('all_lot')
    def _onchange_all_lot(self):
        for rec in self:
            if rec.all_lot:
                rec.lot_ids = self.env['stock.production.lot'].search([]).ids
            else:
                rec.lot_ids = False

    @api.onchange('product_ids')
    def _onchange_product_ids(self):
        for rec in self:
            return {'domain':{'lot_ids':[('product_id','in',self.product_ids.ids)]}}

    @api.onchange('all_product')
    def _onchange_(self):
        for rec in self:
            if rec.all_product:
                rec.product_ids = self.env['product.product'].search([]).ids
                rec.lot_ids = self.env['stock.production.lot'].search([]).ids
            if rec.all_product == False:
                rec.product_ids = False
            
    @api.onchange("date_range_id")
    def _onchange_date_range_id(self):
        self.date_from = self.date_range_id.date_start
        self.date_to = self.date_range_id.date_end

    def button_export_html(self):
        self.ensure_one()
        action = self.env.ref("stock_card_report.action_report_stock_card_report_html")
        vals = action.sudo().read()[0]
        context = vals.get("context", {})
        if context:
            context = safe_eval(context)
        model = self.env["report.stock.card.report"]
        report = model.create(self._prepare_stock_card_report())
        context["active_id"] = report.id
        context["active_ids"] = report.ids
        vals["context"] = context
        return vals

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)

    def _prepare_stock_card_report(self):
        self.ensure_one()
        return {
            "date_from": self.date_from,
            "date_to": self.date_to or fields.Date.context_today(self),
            "product_ids": [(6, 0, self.product_ids.ids)],
            "lot_ids" : [(6, 0, self.lot_ids.ids)],
            "location_id": self.location_id.id,
        }

    def _export(self, report_type):
        model = self.env["report.stock.card.report"]
        report = model.create(self._prepare_stock_card_report())
        return report.print_report(report_type)
