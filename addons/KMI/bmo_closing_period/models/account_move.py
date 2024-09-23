from odoo.exceptions import UserError
from odoo import api, models, _, fields, osv



class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_period(self):
        no = False
        period = self.env['account.period'].find()
        if period:
            no = period.id
        return no

    period_id = fields.Many2one(
        'account.period', 'Period', readonly=True, default=_get_period, domain=[('state', '=', 'draft')], states={'draft':[('readonly', False)]}
    )


    @api.model
    def create(self, vals):
        date = vals.get('date')
        move_type = ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt')
        period = self.env['account.period'].find(date=date)

        move = super(AccountMove, self.with_context(check_move_validity=False, partner_id=vals.get('partner_id'))).create(vals)
        if not period and move.move_type not in move_type:
            raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % date))
        # move.assert_balanced()
        return move
    
    def action_post(self):
        for rec in self:
            date = rec.date
            period = rec.env['account.period'].find(date=date)
            if not period:
                raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % date))
            return super(AccountMove, self).action_post()
        
    def button_cancel(self):
        for rec in self:
            date = rec.date
            period = rec.env['account.period'].find(date=date)
            if not period:
                raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % date))
            return super(AccountMove, self).button_cancel()

    @api.onchange('date', 'period_id')
    def date_change(self):
        res = {'value': {}, 'warning': {}}
        if self.date and self.move_type not in ('out_invoice','in_invoice'):  # self.env.uid
            period = self.env['account.period'].find(date=self.date)
            if period:
                res['value']['period_id'] = period.id
            else:
                res['value']['date'] = fields.Date.context_today(self)
                res['value']['period_id'] = False
                res['warning'] = {'title': 'Warning', 'message': 'There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % self.date}
        return res

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Journal Entries'),
            'template': '/bmo_account_period/static/xls/journal_entries.xls'
        }]


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    period_id = fields.Many2one('account.period', string='Period', related='move_id.period_id', index=True, store=True)

# class AccountInvoice(models.Model):
#     _inherit = 'account.invoice'
#
#     period_id = fields.Many2one('account.period', 'Period', domain=[('state', '=', 'draft')])

