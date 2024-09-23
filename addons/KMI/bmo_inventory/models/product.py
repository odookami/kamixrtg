from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class ProductCategory(models.Model):
    _inherit = 'product.category'

    active = fields.Boolean(default=True)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    expiration_month = fields.Integer(string='Expiration Month',
        help='Number of month after the receipt of the products (from the vendor'
        ' or in stock after production) after which the goods may become dangerous'
        ' and must not be consumed. It will be computed on the lot/serial number.')
    alis_name = fields.Char("Alias Name")
    alias = fields.Char('Alias Code')
    
    @api.constrains('default_code')
    def _check_default_code(self):
        for rec in self:
            if rec.default_code:
                if rec.search([('default_code', '=', rec.default_code),('id', '!=', rec.id)]):
                    raise ValidationError(_('Internal Reference Tidak Boleh Sama !!!!'))
    
    reservation_count = fields.Float(
        compute="_compute_reservation_count", string="# Transfer"
    )

    def _compute_reservation_count(self):
        for product in self:
            product.reservation_count = sum(
                product.product_variant_ids.mapped("reservation_count")
            )

    def action_view_reservations(self):
        self.ensure_one()
        ref = "bmo_inventory.stock_move_line_action_new"
        product_ids = self.mapped("product_variant_ids.id")
        action_dict = self.env.ref(ref).sudo().read()[0]
        sml = self.env['stock.move.line'].sudo().search([("product_id", "in", product_ids),('state','not in',('draft','cancel','done'))])
        action_dict["domain"] = [("id", "in", sml.ids)]
        return action_dict

class Product(models.Model):
    _inherit = 'product.product'

    reservation_count = fields.Float(
        compute="_compute_reservation_count", string="# Transfer"
    )

    def _compute_reservation_count(self):
        for product in self:
            reservations = self.env["stock.move.line"].sudo().search([("product_id", "=", self.id),('state','not in',('draft','cancel','done'))])
            product.reservation_count = sum(reservations.mapped("product_qty"))

    def action_view_reservations(self):
        self.ensure_one()
        ref = "bmo_inventory.stock_move_line_action_new"
        action_dict = self.env.ref(ref).sudo().read()[0]
        sml = self.env['stock.move.line'].sudo().search([("product_id", "=", self.id),('state','not in',('draft','cancel','done'))])
        action_dict["domain"] = [("id", "in", sml.ids)]
        return action_dict
    