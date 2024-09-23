from odoo import _, api, fields, models
from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG
from odoo.exceptions import UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, float_is_zero

class Inventory(models.Model):
    _inherit = 'stock.inventory'

    state = fields.Selection(selection_add=[('approve', 'Confirmed'),('done', 'Done')])
    gain_or_loss = fields.Boolean("Gain/ Loss")
    location_ids = fields.Many2many(
        'stock.location', string='Locations',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit', 'view'])]")
    
    def action_approve(self):
        for rec in self:
            rec.write({'state' : 'approve'})
            return True

    def action_validate(self):
        if self.state == 'confirm':
            self.action_approve()
        else:
            # return super(Inventory, self).action_validate()
            if not self.exists():
                return
            self.ensure_one()
            if not self.user_has_groups('stock.group_stock_manager'):
                raise UserError(_("Only a stock manager can validate an inventory adjustment."))
            # if self.state != 'confirm':
            #     raise UserError(_(
            #         "You can't validate the inventory '%s', maybe this inventory "
            #         "has been already validated or isn't ready.", self.name))
            inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot', 'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
            lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1, precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
            if inventory_lines and not lines:
                wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in inventory_lines.mapped('product_id')]
                wiz = self.env['stock.track.confirmation'].create({'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
                return {
                    'name': _('Tracked Products in Inventory Adjustment'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'views': [(False, 'form')],
                    'res_model': 'stock.track.confirmation',
                    'target': 'new',
                    'res_id': wiz.id,
                }
            self._action_done()
            self.line_ids._check_company()
            self._check_company()
            return True
    
    def action_cancel_draft(self):
        if self.state == 'approve':
            self.write({'state': 'confirm'})
        else:
            return super(Inventory, self).action_cancel_draft()