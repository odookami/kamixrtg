from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    
    # partner_id = fields.Many2one("res.par tner", string='Partner')
    picking_id = fields.Many2one('stock.picking',string='Picking')
    karantina = fields.Boolean(string='Karantina',)
    qty_karantina = fields.Float(string='Qty Karantina',)
    name = fields.Char(
        'Lot/Serial Number', default=lambda self: self.env['ir.sequence'].next_by_code('stock.lot.serial'),
        required=True, help="Unique Lot/Serial Number", tracking=True)
    active = fields.Boolean('Active', default=True)

    def arcive_lot(self):
        for rec in self:
            quant = self.env['stock.quant'].search([('lot_id','=',rec.id)])
            if not quant:
                rec.write({'active' : False})
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(StockProductionLot, self).create(vals_list)
        src_lot = self.search([('name', '=', res.name),('product_id','=',res.product_id.id)])
        print(src_lot)
        print([a.name for a in src_lot])
        if len(src_lot) > 1:
            raise ValidationError(_('Lot Number Sudah Ada'))
        return res 
        
    @api.constrains('name', 'product_id', 'company_id')
    def _check_unique_lot(self):
        domain = [('product_id', 'in', self.product_id.ids),
                  ('company_id', 'in', self.company_id.ids),
                  ('name', 'in', self.mapped('name'))]
        fields = ['company_id', 'product_id', 'name']
        groupby = ['company_id', 'product_id', 'name']
        records = self.read_group(domain, fields, groupby, lazy=False)
        error_message_lines = []
        for rec in records:
            if rec['__count'] != 1:
                product_name = self.env['product.product'].browse(rec['product_id'][0]).display_name
                product_id = self.env['product.product'].browse(rec['product_id'][0])
                if product_id.tracking == 'serial':
                    error_message_lines.append(_(" - Product: %s, Serial Number: %s", product_name, rec['name']))
        if error_message_lines:
            raise ValidationError(_('The combination of serial number and product must be unique across a company.\nFollowing combination contains duplicates:\n') + '\n'.join(error_message_lines))

    def name_get(self):
        res = []
        for rec in self:
            name = str(rec.name)
            if rec.karantina:
                name += " (Quarantine)"
            res.append((rec.id, name))
        return res