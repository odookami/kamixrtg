# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class MrpProductonPackingReport(models.Model):
    _name = 'mrp.production.packing.report'
    _description = 'Laporan Hasil Produksi'

    name = fields.Char(string='Name', default='LHP/')
    state = fields.Selection(string='Status', selection=[('draft', 'Draft'), 
        ('in_progress', 'In Progress'), ('done', 'Done'),], default='draft')
    
    # * BHP 
    mrp_packing_id = fields.Many2one('mrp.production.packing', 
        string='BHP', copy=False)
    item_code = fields.Char(related='product_id.code', string='Item Code')
    product_id = fields.Many2one(related='mrp_packing_id.product_id')
    bo_seq_no = fields.Char(string='Nomor Urut BO', compute='_get_seq_bo')
    lot_producing_id = fields.Many2one(related='mrp_packing_id.lot_producing_id')
    
    mrp_packing_line = fields.One2many('mrp.production.packing.line', 
        inverse_name='mrp_packing_id', string='Detail Bukti Hasil Packing')

    def _get_seq_bo(self):
        for record in self:
            result = False
            if record.production_id:
                result = str(record.production_id.bo_id.name)[5]
            record.bo_seq_no = result
    
    # * Manual Input - Admin Shift
    final_code = fields.Char(string='Kode Body Botol Final')
    retort_seq_no = fields.Char(string='NO Urutan Retort')			

    # * BHP	
    okp_id = fields.Many2one(related='mrp_packing_id.okp_id', store=True)
    
    #  * Manual Input- PPIC
    bo_filling = fields.Char(string='BO FILLING')
    bo_banded = fields.Char(string='BO BANDED')
    # bo_filling_id = fields.Many2one('mrp.production', string='BO FILLING')
    # bo_banded_id = fields.Many2one('mrp.production', string='BO BANDED')

    # * new and computed fields
    exp_in_month = fields.Char(string='EXP (BULAN)', compute='_compute_exp_date')

    @api.depends('lot_producing_id')
    def _compute_exp_date(self):
        for record in self:
            result = ''
            if record.product_id.expiration_time:
                exp_time = record.product_id.expiration_time
                result = round(exp_time/30) # * assuming 30 days for 1 month
                # lot_exp_date = record.lot_producing_id.expiration_date
                # exp_date = lot_exp_date - fields.Date.today()
                # print(lot_exp_date, "###LED###")
                # print(exp_date, "###ED###")
            record.exp_in_month = str(result or '')
    
    #  * Manual Input - PPIC
    po_fee = fields.Char(string='PO FEE')
    
    #  * Manual Input - Mixing - QTY Mixing - Admin Shift
    plan_date_mixing = fields.Date(string='Plan date')
    actual_date_mixing = fields.Date(string='Actual date')
    output_mixing = fields.Float(string='Output Mixing (L)')

    # * Manual Input - Packing - Admin Shift
    plan_date_packing = fields.Date(string='Plan date ')
    actual_date_packing = fields.Date(string='Actual date ')

    # * BHP and Function
    expiration_date = fields.Datetime(related='lot_producing_id.expiration_date')
    total_output_packing = fields.Float(string='Total Output (pcs)', compute='_compute_top')

    @api.depends('cb_packing', 'pcs_packing')
    def _compute_top(self):
        for record in self:
            result = (record.cb_packing * 36) + record.pcs_packing
            record.total_output_packing = result if result > 0 else 0

    total_bo_packing = fields.Float(string='Total/BO', compute='_compute_bop')

    @api.depends('mrp_packing_id')
    def _compute_bop(self):
        for record in self:
            result = 0
            # if record.mrp_packing_id:
            #     # ToDo: find BO mrp
            #     result = sum([x.quantity for x in record.mrp_packing_id.production_id.bo_id])
            record.total_bo_packing = result if result > 0 else 0

    # current_location_id = fields.Many2one(related='mrp_packing_id.location_dest_id', string='Locator')

    # * Manual Input - Sample QC - QC
    total_sample_qc = fields.Float(string='Sample QC')

    # * Manual Input - Sortir 1	- Admin Shift
    plan_date_sortir1 = fields.Date(string='Plan Date')
    actual_date_sortir1 = fields.Date(string='Actual date 1')
    cb_sortir1 = fields.Float(string='CB  ')
    pcs_sortir1 = fields.Float(string='PCS')
    total_pcs_sortir1 = fields.Float(string='Total pcs/lot')
    total_sortir1 = fields.Float(string='TOTAL')

    # * Manual Input - Sortir 2	- 	Admin Shift
    plan_date_sortir2 = fields.Date(string='Plan Date ')
    actual_date_sortir2 = fields.Date(string='Actual date 1 ')
    cb_sortir2 = fields.Float(string='CB ')
    pcs_sortir2 = fields.Float(string='PCS ')
    total_pcs_sortir2 = fields.Float(string='Total pcs/lot ')
    total_sortir2 = fields.Float(string='TOTAL ')

    # * Function - actual sortir	
    actual_date_acs = fields.Date(string='Actual Date ', compute='_get_actual_date_acs')
    
    # @api.depends('plan_date_sortir1', 'plan_date_sortir2')
    def _get_actual_date_acs(self):
        for record in self:
            result = False
            actual_dates = []
            actual_dates.append(record.actual_date_sortir1) \
                if record.actual_date_sortir1 else None
            actual_dates.append(record.actual_date_sortir2) \
                if record.actual_date_sortir2 else None
            # print(actual_dates, "###A###")
            result = max(actual_dates) if actual_dates else False
            # print(result, "###R###")
            record.actual_date_acs = result

    cb_acs = fields.Float(string='Qty Akhir CB')
    pcs_acs = fields.Float(string='Qty Akhir PCS ')
    total_pcs_acs = fields.Float(string='Total Pcs/lot ')
    total_reject_acs = fields.Float(string='TOTAL reject sortir')

    # * Manual Input - TIME - Admin Shift
    plan_date = fields.Date(string='Time - Plan date')
    actual_date	= fields.Date(string='Time - Actual date')

    # * BHP	- Banded - QTY Banded	
    cb_banded = fields.Float(string='CB Banded')
    pcs_banded = fields.Float(string='PCS Banded')

    # * Function - Banded - QTY Banded
    total_pcs_banded = fields.Float(string='Total Pcs/Lot ')
    total_banded = fields.Float(string='Total')
    reject_banded = fields.Float(string='Reject')

    # * BHP
    bhp_state = fields.Selection(related='mrp_packing_id.state')

    # * Function - ALOKASI	
    # picking_id = fields.Many2one(related='mrp_packing_id.picking_id', string='No Alokasi')
    # picking_qty = fields.Float(string='Qty', compute='_compute_picking_qty')

    # def _compute_picking_qty(self):
    #     for record in self:
    #         result = 0
    #         if record.order_id:
    #             move_ids = record.picking_id.move_ids_without_package
    #             result = sum(x.quantity_done for x in move_ids)
    #         record.picking_qty = result

    is_match = fields.Boolean(string='Sesuai', compute='_compute_is_match')

    def _compute_is_match(self):
        for record in self:
            result = [x.id for x in record.order_id.order_line \
                if x.product_uom_qty == x.qty_delivered]
            record.is_match = True if result is not False else False

    picking_date = fields.Datetime(related='picking_id.scheduled_date', string='Waktu')

    # * Function - Actual Kirim	
    delivery_ids = fields.Many2many('stock.picking', string='NO DO', 
        compute='_get_order_delivery')
    # TANGGAL
    # QTY
    @api.depends('order_id')
    def _get_order_delivery(self):
        for record in self:
            result = []
            if record.order_id:
                result = [(6, 0, record.order_id.picking_ids.ids)]
            record.delivery_ids = result

    # * Manual Input -PPIC
    remaining_stock = fields.Float(string='SISA STOCK')
    plan_delivery = fields.Char(string='PLANNING DELIVERY')
    remarks_1st = fields.Char(string='REMAKS')
    now = fields.Char(string='NOW')
    lead_time = fields.Char(string='LEAD TIME')
    status_ppic = fields.Char(string='STATUS')
    remarks_2nd = fields.Float(string='REMAKS ')

    # * Function - SAMPLE MARKETING	
    order_id = fields.Many2one('sale.order', string='No DO')
    order_qty = fields.Float(string='Qty ', compute='_compute_order_qty')

    def _compute_order_qty(self):
        for record in self:
            result = 0
            if record.order_id:
                result = sum(x.product_uom_qty for x in record.order_id.order_line)
            record.order_qty = result

    order_date = fields.Datetime(related='order_id.date_order', string='Waktu ')

    # * Manual Input - PPIC
    fup_no = fields.Char(string='NO FUP')
    bbk = fields.Char(string='BBK')

    # * Function			
    order_total = fields.Float(string='Total ', compute='_compute_order_total')

    def _compute_order_total(self):
        for record in self:
            result = 0
            if record.order_id:
                result = sum(x.price_subtotal for x in record.order_id.order_line)
            record.order_total = result

    # * Manual Input - PPIC		
    saldo_sm = fields.Float(string='Saldo')

    def write(self, vals):
        self._check_access(v for v in vals.keys())
        return super(MrpProductonPackingReport, self).write(vals)

    def _check_access(self, field):
        module = 'bmo_mrp_packing.'
        access_dict = {
                'groups_lhp_admin_shift': ['final_code', 'retort_seq_no',
                    'plan_date_banded', 'actual_date_banded', 
                    'plan_date_mixing', 'actual_date_mixing', 
                    'output_mixing', 'plan_date_packing', 'actual_date_packing', 
                    'plan_date_sortir1', 'actual_date_sortir1', 'cb_sortir1',
                    'pcs_sortir1', 'total_pcs_sortir1', 'total_sortir1',
                    'plan_date_sortir2', 'actual_date_sortir2', 'cb_sortir2',
                    'pcs_sortir2', 'total_pcs_sortir2', 'total_sortir2',
                    ],
                'groups_lhp_ppic': ['remaining_stock', 'plan_delivery', 'remarks_1st', 
                    'now', 'lead_time', 'status_ppic', 'remarks_2nd', 'no_fup', 'bbk'],
                'groups_lhp_qc': ['sample_qc'],
            
            }
        access_groups = [k for k in access_dict.keys()]
        has_access_groups = [self.env.user.has_group(module + k) for k in access_dict.keys()]

        # print(access_groups, "###AG###")
        # print(has_access_groups, "###HA###")

        access_fields = []
        list_fields = [access_fields + v for v in access_dict.values()]
        # for lst in list_fields:

        # print(list_fields, "###LF###")
        # print(has_access, "###HA###")

        if True not in has_access_groups:
            raise ValidationError('You are not allowed to update the record !')

