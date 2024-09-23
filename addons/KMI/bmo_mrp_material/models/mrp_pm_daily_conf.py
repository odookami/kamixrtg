from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError

class mrp_pm_daily(models.Model):
    _name = 'mrp.pm.daily'
    _description = 'Config PM Harian'

    name = fields.Char(
        string='Name', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    date = fields.Date(
        "Date", states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    state = fields.Selection([
        ('draft','Draft'),('done','Done'),('cancel','Cancel')], readonly=True, string="Status", default='draft')
    conf_line = fields.One2many(
        'mrp.pm.daily.line', 'pm_harian_id', string='Config Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)
    
    def action_done(self):
        for rec in self:
            src_data = rec.search([('state','=','draft'),('id','!=',rec.id)])
            if src_data:
                raise UserError(_('Tidak Boleh Ada status done lebih dari 1 !'))
            rec.update({'state' : 'done'})

    def action_set_draft(self):
        for rec in self:
            rec.update({'state' : 'draft'})

    def action_cancel(self):
        for rec in self:
            rec.update({'state' : 'cancel'})

    def unlink(self):
        for rec in self:
            if rec.state == 'done':
                raise UserError(_('Tidak Bisa di hapus jika status sudah Done.'))
        return super(mrp_pm_daily, self).unlink()

class mrp_pm_daily_line(models.Model):
    _name = 'mrp.pm.daily.line'
    _description = 'Config PM Harian Line'
    rec_name = 'product_id'

    pm_harian_id = fields.Many2one(
        'mrp.pm.daily', string='PM Harian Config', required=True, ondelete='cascade', index=True, copy=False
    )
    product_id = fields.Many2one(
        'product.product', 'Product', domain="[('type','=','product')]"
    )
    lot_id = fields.Many2one(
        "stock.production.lot", 'Lot Number', domain="[('product_id','=', product_id)]"
    )
    qty = fields.Float(
        "Qty", digits='Product Unit of Measure'
    )