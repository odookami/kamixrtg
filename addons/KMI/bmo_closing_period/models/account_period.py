from datetime import datetime
from dateutil.relativedelta import relativedelta
import odoo
from odoo import api, models, _, fields
from odoo.osv import expression

state_status = [('sale','Sales'),('mrp','Manufacturing'),('inventory','Inventory'),('accounting','Accounting')]

class account_fiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"
    _order = "date_start, id"

    name = fields.Char(
        'Fiscal Year', required=True)
    code = fields.Char(
        'Code', size=6, required=True)
    interval = fields.Char(
        'Interval')
    company_id = fields.Many2one(
        'res.company', 'Company', required=True, default=lambda self: self.env.user.company_id)
    date_start = fields.Date(
        'Start Date', required=True)
    date_stop = fields.Date(
        'End Date', required=True)
    period_ids = fields.One2many(
        'account.period', 'fiscalyear_id', 'Periods')
    state = fields.Selection(
        [('draft', 'Open'), ('done', 'Closed')], 'Status', readonly=True, copy=False, default='draft')
    type = fields.Selection(state_status, string='Type', required=True)
    

    def create_period3(self):
        self.interval = 3
        return self.create_period()

    
    def create_period(self):
        if not hasattr(self,'interval'):
            self.interval = 1
        period_obj = self.env['account.period']
        for fy in self.browse(self.ids):
            ds = fy.date_start
            period_obj.create({
                    'name'          :  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
                    'code'          : ds.strftime('00/%Y'),
                    'date_start'    : ds,
                    'date_stop'     : ds,
                    'special'       : True,
                    'type'          : fy.type,
                    'fiscalyear_id' : fy.id,
                    'state'         : 'done',
                })
            date = fy.date_stop.month - ds.month
            for x in range(date+1):
                de = ds + relativedelta(months=1) - relativedelta(days=1)
                period_obj.create({
                    'name'          : ds.strftime('%m/%Y'),
                    'code'          : ds.strftime('%m/%Y'),
                    'date_start'    : ds.strftime('%Y-%m-%d'),
                    'date_stop'     : de.strftime('%Y-%m-%d'),
                    'fiscalyear_id' : fy.id,
                    'type'          : fy.type,
                    'state'         : 'done',
                })
                ds = ds + relativedelta(months=1) 
        return True


class AccountPeriod(models.Model):
    _name = "account.period"
    _description = "Account period"
    _order = "date_start, special desc"

    name = fields.Char('Period Name', required=True)
    code = fields.Char('Code', size=12)
    special = fields.Boolean('Opening/Closing Period', help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True, states={'done': [('readonly', True)]})
    date_stop = fields.Date('End of Period', required=True, states={'done': [('readonly', True)]})
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'Fiscal Year', ondelete='cascade', required=True, states={'done': [('readonly', True)]}, index=True)
    state = fields.Selection([('draft', 'Open'), ('done', 'Closed')], 'Status', readonly=True, copy=False, default='draft', help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
    company_id = fields.Many2one('res.company', related='fiscalyear_id.company_id', string='Company', store=True, readonly=True)
    type = fields.Selection(state_status, string='Type', required=True)


    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, type)', 'The name of the period must be unique per company!'),
    ]

    
    def _check_duration(self):
        for period in self:
            if period.date_stop < period.date_start:
                return False
        return True

    
    def _check_year_limit(self):
        for period in self:
            if period.fiscalyear_id.date_stop < period.date_stop or \
               period.fiscalyear_id.date_stop < period.date_start or \
               period.fiscalyear_id.date_start > period.date_start or \
               period.fiscalyear_id.date_start > period.date_stop:
                return False

        return True

    _constraints = [
        (_check_duration, 'Error!\nThe duration of the Period(s) is/are invalid.', ['date_stop']),
        (_check_year_limit, 'Error!\nThe period is invalid. Either some periods are overlapping or the period\'s dates are not matching the scope of the fiscal year.', ['date_stop'])
    ]

    @api.model
    def find(self, date=None, company_id=None, tipe=None):
        if not date:
            date = fields.Date.today(self)

        args = [('date_start', '<=', date), ('date_stop', '>=', date), ('state', '=', 'draft'), ('type', '=', tipe)]
        if company_id:
            args.append(('company_id', '=', company_id))
        else:
            args.append(('company_id', '=', self.env.user.company_id.id))

        result = self.search(args, limit=1)
        if not result:
            result = False
        return result

    
    def action_draft(self):
        for period in self:
            if period.fiscalyear_id.state == 'done':
                raise UserError(("Period tidak bisa di open lagi karna fiscal year telah close"))
            period.write({'state': 'draft'})
        return True

    
    def action_done(self):
        for period in self:
            if period.type not in  ('sale','mrp','inventory'):
                move_ids = self.env['account.move'].search([('period_id', '=', period.id), ('state', '=', 'draft'),('move_type', 'not in', ('out_invoice','in_invoice'))])
                if move_ids:
                    raise UserError(("Period tidak bisa di close karna masih ada journal entris yang belum di posting"))
            period.write({'state': 'done'})
        return True

    # def name_get(self):
    #     return [(period.id, '%s%s' % (period.code and '[%s] ' % period.code or '', period.name)) for period in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = ['|', ('code', operator, name), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()
