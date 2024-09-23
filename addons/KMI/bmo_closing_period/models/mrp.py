from datetime import timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date 

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def _get_period(self):
        no = False
        period = self.env['account.period'].find(self.actual_complete_date, self.env.company.id, 'mrp')
        if period:
            no = period.id
        return no

    period_id = fields.Many2one(
        'account.period', 'Period', readonly=True, default=_get_period, domain=[('state', '=', 'draft')], states={'draft':[('readonly', False)]}
    )

    @api.model
    def create(self, vals):
        dt = self.actual_complete_date
        period = self.env['account.period'].find(dt, self.env.company.id, 'mrp')

        res = super(MrpProduction, self).create(vals)
        if not period:
            raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % dt))
        return res
    
    def write(self, values):
        for rec in self:
            dt = rec.actual_complete_date
            period = self.env['account.period'].find(dt, self.env.company.id, 'mrp')
            if not period:
                raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % dt))
        return super(MrpProduction, self).write(values)

class StockMove(models.Model):
    _inherit = 'stock.move'

    period_mrp_id = fields.Many2one('account.period', string='Period', related='raw_material_production_id.period_id', index=True, store=True)