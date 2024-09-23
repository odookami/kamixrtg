# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions

class MrpProductonPacking(models.Model):
    _inherit = 'mrp.production.packing'
    # _order = 'date desc, name asc'
    _order = 'name desc, date desc'

    sort_finished = fields.Boolean()

class MrpProductonPackingLine(models.Model):
    _inherit = 'mrp.production.packing.line'

    sort_finished = fields.Boolean()

class MrpSortir(models.Model):
    _name = 'mrp.sortir.report'
    _description = 'Laporan Sortir'

    active = fields.Boolean(default=True)
    product_id = fields.Many2one('product.product', 
        string='Item Name', required=True)
    name = fields.Char(string='Item Code', related='product_id.default_code')
    lot_producing_id = fields.Many2one('stock.production.lot', 
        string='Item Lot', required=True)
    package_id = fields.Many2one('stock.quant.package', 
        string='No Urut Pallet', required=True)
    sort_seq = fields.Selection(string='Sortir Ke-', 
        selection=[('1', '1'), ('2', '2')], required=True)
    actual_date = fields.Date(string='Actual Date', required=True)
    output_cb = fields.Float(string="CB", help='Output CB', required=True)
    output_pcs = fields.Float(string="PCS", help='Output PCS', required=True)
    output_total = fields.Float(string="TOTAL", help='Output TOTAL PCS/LOT', required=True)
    # compute_bhp = fields.Many2one('mrp.production.packing', compute='_get_mrp_packing')
    mrp_packing_id = fields.Many2one('mrp.production.packing', string='BHP Packing')
    mrp_packing_line_id = fields.Many2one('mrp.production.packing.line', string='BHP Packing Line')

    def _get_possible_lots(self, product_id, lot_name):
        lot_ids = []
        lot_obj = self.env['stock.production.lot']
        lot_dom = [
            ('name', '=', lot_name), 
            ('product_id', '=', product_id.id), 
        ]
        lot_ids = lot_obj.search(lot_dom)
        # print(lot_dom, '###LOTS###', lot_ids, '\n')
        return lot_ids

    def _get_bhp(self, product_id, lot_id, actual_date, package_id):
        result = {}
        bhp_ids = []
        product_obj = self.env['product.product']
        lot_obj = self.env['stock.production.lot']
        pack_obj = self.env['stock.quant.package']
        bhp_obj = self.env['mrp.production.packing']

        lot_ids = self._get_possible_lots(
            product_obj.browse([product_id]), 
            lot_obj.browse([lot_id]).name
        )
        bhp_dom = [
            ('state', '=', 'done'),
            ('date', '<=', actual_date), 
            # ('sort_finished', '!=', True), 
            ('packing_type', '=', 'Filling'),
            ('mrp_packing_line', '!=', False), 
            ('lot_producing_id', 'in', lot_ids.ids),
            ('product_id', '=', product_obj.browse([product_id]).id), 
        ]
        bhp_ids = bhp_obj.search(bhp_dom)
        # print(bhp_dom, [x.name for x in bhp_ids], "###BHPS###", '\n')
        if not bhp_ids:
            message = 'Tidak ditemukan BHP Packing untuk data Sortir tersebut !'
            raise exceptions.ValidationError(message)

        for bhp in bhp_ids:
            pack_id = pack_obj.browse([package_id])
            pack_line = bhp.mrp_packing_line.filtered(
                lambda x: x.package_id.name == pack_id.name)
            if not pack_line:
                message = 'No Urut Pallet tidak sesuai dengan BHP !'
                raise exceptions.ValidationError(message)

            sorted_pack_line = [x for x in pack_line if x.sort_finished]
            if sorted_pack_line:
                message = 'Product dengan Lot dan Pallet tsb sudah disortir !'
                raise exceptions.ValidationError(message)

            result['bhp_line_id'] = pack_line
        
        result['bhp_ids'] = bhp_ids
        print(result, "###R###")

        return result

    @api.model
    def create(self, values):
        # Add code here
        # print(values, "###V###")
        data_bhp_ids = self._get_bhp(values['product_id'], values['lot_producing_id'], 
            values['actual_date'], values['package_id'])
        bhp_id = data_bhp_ids['bhp_ids'][-1]
        bhp_line_id = data_bhp_ids['bhp_line_id'][-1]
        values['mrp_packing_id'] = False if not bhp_id else bhp_id.id
        values['mrp_packing_line_id'] = False if not bhp_line_id else bhp_line_id.id
        return super(MrpSortir, self).create(values)

    # @api.depends('product_id')
    def _compute_hide_btn_create(self):
        for record in self:
            record.hide_btn_create = """
                <style>.o_list_button_add {display: none !important;}</style>
            """
            # print(record.hide_btn_create, "###record.hide_btn_create###")

    hide_btn_create = fields.Html(string='', sanitize=False, 
        compute='_compute_hide_btn_create', store=False)

    state = fields.Selection(string='Status', selection=[('in_progress', 'In Progress'), 
        ('hold', 'Hold'), ('reject', 'Rejected'), ('done', 'Done'), 
        ('revisi', 'Revisi')], default='in_progress', tracking=True)

    def action_done(self):
        for record in self:
            record.mrp_packing_line_id.write({'sort_finished': True})
        return self.write({'state': 'done'})
    
    def unlink(self):
        # Add code here
        for record in self:
            if record.state == 'done':
                message = "Data Sortir pada status 'Done' tidak bisa dihapus !"
                raise exceptions.ValidationError(message)
        return super(MrpSortir, self).unlink()
    
    