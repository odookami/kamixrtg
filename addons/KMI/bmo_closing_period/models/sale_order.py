from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date 


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_period(self):
        no = False
        period = self.env['account.period'].find(date.today(), self.env.company.id, 'sale')
        if period:
            no = period.id
        return no

    period_id = fields.Many2one(
        'account.period', 'Period', readonly=True, default=_get_period, domain=[('state', '=', 'draft')], states={'draft':[('readonly', False)]}
    )

    @api.model
    def create(self, vals):
        dt = date.today()
        period = self.env['account.period'].find(dt, self.env.company.id, 'sale')

        res = super(SaleOrder, self).create(vals)
        if not period:
            raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % dt))
        return res
    
    def write(self, values):
        dt = date.today()
        period = self.env['account.period'].find(dt, self.env.company.id, 'sale')

        res = super(SaleOrder, self).write(values)
        if not period:
            raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % dt))
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    period_id = fields.Many2one('account.period', string='Period', related='order_id.period_id', index=True, store=True)