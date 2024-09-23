from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date 

class Picking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def _get_period(self):
        no = False
        period = self.env['account.period'].find(date.today(), self.env.company.id, 'inventory')
        if period:
            no = period.id
        return no

    period_id = fields.Many2one(
        'account.period', 'Period', readonly=True, default=_get_period, domain=[('state', '=', 'draft')], states={'draft':[('readonly', False)]}
    )

    @api.model
    def create(self, vals):
        dt = date.today()
        period = self.env['account.period'].find(dt, self.env.company.id, 'inventory')

        res = super(Picking, self).create(vals)
        if not period:
            raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % dt))
        return res
    
    def write(self, values):
        dt = date.today()
        period = self.env['account.period'].find(dt, self.env.company.id, 'inventory')

        res = super(Picking, self).write(values)
        if not period:
            raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % dt))
        return res

class StockMove(models.Model):
    _inherit = "stock.move"

    period_id = fields.Many2one('account.period', string='Period', related='picking_id.period_id', index=True, store=True)