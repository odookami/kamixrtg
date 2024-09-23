# Copyright YEAR(S), AUTHOR(S)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api, _

class QualityCheckFinishGood(models.Model):
    _name = 'quality.check.finish.good'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Quality Check Finish Good'

    name = fields.Char(string='Number', default='New')
    warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse',)
    location_id = fields.Many2one('stock.location',string='View Location', domain=[('usage', '=', 'view')])
    product_id = fields.Many2one('product.product',string='Product', related='lot_id.product_id')
    lot_id = fields.Many2one('stock.production.lot',string='Lot Number',)
    prod_packing_id = fields.Many2one('mrp.production.packing',string='BHP',)
    qcfg_line = fields.One2many('quality.check.finish.good.line','qcfg_id',string='Field Label', tracking=True)
    note = fields.Text(string='Notes',)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('progress', 'In Progress'),
        ('done', 'Done'),], default='draft', string='Status',tracking=True)
    company_id = fields.Many2one('res.company',string='Company', default=lambda self:self.env.company)
    scrap = fields.Boolean(string='Scrap',)

    def button_scrap(self):
        self.ensure_one()
        return {
            'name': _('Scrap'),
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {
                'default_production_id': self.id,
                # 'product_ids': (self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids,
                'default_company_id': self.company_id.id
                        },
            'target': 'new',
        }

    @api.model
    def create(self,vals):
        # vals['name'] = vals.get
        res = super(QualityCheckFinishGood, self).create(vals)
        res.name = res.lot_id.name + '/QCFG' if res.lot_id else '/'
        return res

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        self.prod_packing_id = False
        if self.lot_id:
            # Harus dipastikan 1 BHP hanya untuk 1 lot number saja
            bhp_id = self.env['mrp.production.packing'].search([('lot_producing_id', '=', self.lot_id.id), ('state', '=', 'done'), ('packing_type', '=', 'Banded')], limit=1)
            self.prod_packing_id = bhp_id.id if bhp_id else False

    @api.onchange('prod_packing_id')
    def _onchange_prod_packing_id(self):
        self.warehouse_id = self.location_id = self.qcfg_line = False
        qc_line = []
        if self.prod_packing_id:
            picking_id = self.prod_packing_id.picking_id
            self.lot_id = self.prod_packing_id.lot_producing_id.id
            self.warehouse_id = self.prod_packing_id.picking_type_id.warehouse_id.id
            self.location_id  = self.prod_packing_id.location_dest_id.id
            for move_line in self.prod_packing_id.mrp_packing_line.filtered(lambda l:not l.checked and l.picking_id):
                qc_line.append((0,0,{
                    'mrp_packing_line_id' 	: move_line.id,
                    'package_id' 		  	: move_line.package_id.id,
                    'location_id' 			: move_line.location_dest_id.id,
                    'lot_id' 				: self.lot_id.id,
                    'qty' 					: move_line.total_output_banded,
                    'state' 				: 'open',
                    }))
        value = {'qcfg_line': qc_line} if qc_line else {}
        return {'value': value}

    def action_done(self):
        return self.write({'state' : 'done'})

    def action_submit(self):
        return self.write({'state' : 'progress'})

    def action_draft(self):
        return self.write({'state' : 'draft'})


    def action_release(self):
        for rec in self:
            location_ids = rec.qcfg_line.mapped('location_id')
            location_ids.write({'quarantine' : False})
            rec.qcfg_line.write({'state' : 'release'})

    def action_hold(self):
        for rec in self:
            location_ids.write({'quarantine' : True})
            rec.qcfg_line.write({'state' : 'hold'})

    def action_reject(self):
        for rec in self:
            rec.qcfg_line.write({'state' : 'reject'})


class QualityCheckFinishGoodLine(models.Model):
    _name = 'quality.check.finish.good.line'
    _description = 'Quality Check Finish Good Line'
    _order = 'package_id asc'

    # number = fields.Char('Number')
    package_id = fields.Many2one('stock.quant.package',string='Pallet',)
    pallet = fields.Char('Pallet')
    qcfg_id = fields.Many2one('quality.check.finish.good',string='QC Finish Good',)
    location_id = fields.Many2one('stock.location',string='Location')
    qty = fields.Float(string='Quantity',)
    lot_id = fields.Many2one('stock.production.lot',string='Lot Number',)
    expired_date = fields.Datetime(string='Expired Date', related='lot_id.expiration_date')
    state = fields.Selection([
        ('open', 'Open'),
        ('release', 'Release'),
        ('hold', 'Hold'),
        ('reject', 'Reject'),], default='open', string='Status', tracking=True)
    mrp_packing_line_id = fields.Many2one('mrp.production.packing.line',string='MRP Packing Line ID',)

    @api.model
    def create(self, vals):
        if vals.get('mrp_packing_line_id'):
            mrp_packing_line_id = self.env['mrp.production.packing.line'].browse([vals.get('mrp_packing_line_id')])
            mrp_packing_line_id.write({'checked' : True})
            # print(mrp_packing_line_id)

        return super(QualityCheckFinishGoodLine, self).create(vals)

    def action_release(self):
        for rec in self:
            rec.write({'state' : 'release'})
            rec.location_id.quarantine = False

    def action_hold(self):
        for rec in self:
            rec.location_id.quarantine = True
            rec.write({'state' : 'hold'})

    def action_reject(self):
        for rec in self:
            rec.write({'state' : 'reject'})


    # def write(self, vals)