# -*- coding: utf-8 -*-

import math
from typing import Tuple, ValuesView
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from datetime import date, datetime, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo.addons.bmo_mrp.models.product import state_tipe
import pytz

class ProductTemplate(models.Model):
    _inherit = "product.template"

    history_cost_line = fields.One2many(
        "product.cost.mrp.history", "product_id", compute='_compute_default_history_cost_line', string="History Cost")
    cost_line_id = fields.Many2one(
        "mrp.valuation.adjustment.lines", "Valuation Adjustments", compute='_compute_default_cost_line', readonly=False)
    
    @api.depends('product_variant_ids', 'product_variant_ids.history_cost_line')
    def _compute_default_history_cost_line(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.history_cost_line = template.product_variant_ids.history_cost_line
        for template in (self - unique_variants):
            template.history_cost_line = False
    
    @api.depends('product_variant_ids', 'product_variant_ids.cost_line_id')
    def _compute_default_cost_line(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.cost_line_id = template.product_variant_ids.cost_line_id.id or False
        for template in (self - unique_variants):
            template.cost_line_id = False
    
class ProductProduct(models.Model):
    _inherit = "product.product"
    
    history_cost_line = fields.One2many(
        "product.cost.mrp.history", "product_id", string="History Cost")
    cost_line_id = fields.Many2one(
        "mrp.valuation.adjustment.lines", "Valuation Adjustments", readonly=False)

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    quantity = fields.Float('Quantity', digits='Product Unit of Measure', help='Quantity', readonly=True)
    unit_cost_new = fields.Float('Unit Value New', readonly=True, digits='Product Price')
    unit_cost = fields.Monetary('Unit Value', readonly=True, digits='Product Price')
    value = fields.Monetary('Total Value', readonly=True, digits='Product Price')
    remaining_qty = fields.Float(readonly=True, digits='Product Unit of Measure')
    remaining_value = fields.Monetary('Remaining Value', readonly=True, digits='Product Price')

class product_cost_mrp_history(models.Model):
    _name = "product.cost.mrp.history"
    _description = 'Product Cost MRP Hisotry'
    _order = "date desc"
    
    name = fields.Char('Name')
    product_id = fields.Many2one('product.product', 'Product')
    lot_ids = fields.Many2many(
        'stock.production.lot',string='Lot Number')
    date = fields.Date("Date")
    unit_price = fields.Float("Unit Cost")

class MRPCost(models.Model):
    _name = 'mrp.cost'
    _description = 'MRP Cost'
    _order = "name desc"
    
    @api.model
    def _default_employee_id(self):
        employee = self.env.user.employee_id
        return employee
    def _default_start_datetime(self):
        return datetime.combine(fields.Datetime.now(), datetime.min.time())

    def _default_end_datetime(self):
        return datetime.combine(fields.Datetime.now(), datetime.max.time()) + relativedelta(months=1) - relativedelta(days=1)
    
    @api.model
    def _get_period(self):
        no = False
        period = self.env['account.period'].find(date.today(), self.env.company.id, 'inventory')
        if period:
            no = period.id
        return no

    name = fields.Char(
        'Name', default=lambda self: _('New'), copy=False, readonly=True)
    period_id = fields.Many2one(
        'account.period', 'Period', readonly=True, default=_get_period, domain=[('state', '=', 'draft')], states={'draft':[('readonly', False)]}
    )
    cost_lines = fields.One2many(
        'mrp.cost.line', 'cost_id', 'Cost Lines', copy=True, states={'done': [('readonly', True)]})
    valuation_adjustment_lines = fields.One2many(
        'mrp.valuation.adjustment.lines', 'cost_id', 'Valuation Adjustments',)
    employee_id = fields.Many2one(
        'hr.employee', string="Employee", readonly=True, default=_default_employee_id)
    state = fields.Selection(
        [('draft', 'Draft'),('done', 'Posted'),('cancel', 'Cancelled')], 'State', default='draft', copy=False, readonly=True)
    tipe = fields.Selection(state_tipe, string='Type')
    date_start = fields.Date(
        'Start Date', default=_default_start_datetime)
    date_end = fields.Date(
        'Start End', default=_default_end_datetime)
    select_month = fields.Selection([
        ("01", "Januari"), 
        ("02", "Februari"), 
        ("03", "Maret"), 
        ("04", "April"),
        ("05", "Mei"),
        ("06", "Juni"),
        ("07", "Juli"),
        ("08", "Agustus"),
        ("09", "September"),
        ("10", "Oktober"),
        ("11", "Nopember"),
        ("12", "Desember"),], string='Month')
    select_year = fields.Selection(
        [(str(num), str(num)) for num in range(2020, (datetime.now().year)+2 )])
    amount_total = fields.Float(
        'Total', compute='_compute_total_amount', digits=0, store=True, track_visibility='always')
    total_machine_usage_time = fields.Float(
        'Waktu Penggunaan mesin', compute='_compute_total_amount', digits=0, store=True)
    stock_valuation_layer_ids = fields.One2many(
        'stock.valuation.layer', 'stock_mrp_cost_id')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)
    batch_ids =  fields.Many2many("batch.mrp.production", string="OKP")
    machine_usage_time = fields.Float(
        'Waktu mesin', compute="_compute_total_valution")
    allocation_ratio = fields.Float(
        'Allocation Ratio', default=0.0, digits=(12,0), compute="_compute_total_valution")
    allocation_fee = fields.Float(
        'Biaya Alokasi', digits=(12, 2), compute="_compute_total_valution")
    biaya_wip = fields.Float(
        'Biaya WIP', digits=(12, 2), compute="_compute_total_valution")
    production_result = fields.Float(
        'Hasil Produksi', compute="_compute_total_valution")
    result_pmac_prod = fields.Float(
        'PMAC*Total Produksi ', compute="_compute_total_valution")
    consum_wip = fields.Float(
        "Consume WIP", compute="_compute_total_valution")
    last_stock_manual = fields.Boolean("Last Stock Manual")
    
    @api.depends('valuation_adjustment_lines.allocation_ratio', 'valuation_adjustment_lines.consum_wip')
    def _compute_total_valution(self):
        for rec in self:
            rec.machine_usage_time = sum(
                rec.valuation_adjustment_lines.mapped('machine_usage_time'))
            rec.allocation_ratio = sum(
                rec.valuation_adjustment_lines.mapped('allocation_ratio'))
            rec.allocation_fee = sum(
                rec.valuation_adjustment_lines.mapped('allocation_fee'))
            rec.biaya_wip = sum(
                rec.valuation_adjustment_lines.mapped('biaya_wip'))
            rec.production_result = sum(
                rec.valuation_adjustment_lines.mapped('production_result'))
            rec.result_pmac_prod = sum(
                rec.valuation_adjustment_lines.mapped('result_pmac_prod'))
            rec.consum_wip = sum(
                rec.valuation_adjustment_lines.mapped('consum_wip'))
                
    @api.depends('cost_lines.price_unit','valuation_adjustment_lines.machine_usage_time')
    def _compute_total_amount(self):
        self.amount_total = sum(line.price_unit for line in self.cost_lines)
        self.total_machine_usage_time = sum(line.machine_usage_time for line in self.valuation_adjustment_lines)
    
    @api.onchange('tipe')
    def _onchange_batch_tipe(self):
        lines = []
        lines_dict = {}
        if self.tipe:
            product = self.env['product.product'].search([('type','=','service')])
            for p in product:
                lines.append((0,0,{
                    'name'      : p.name,
                    'product_id': p.id,
                    'price_unit': p.standard_price or 0,
                }))
            self.cost_lines = False
        value = {'cost_lines': lines} if lines else {}
        return {'value': value}
    
    def button_validate(self):
        user_tz = self.env.user.tz
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(user_tz)
        for rec in self:
            if not rec.valuation_adjustment_lines:
                raise UserError(_('Harap Klik Compute Terlebih Dahulu.'))
            date_1 = datetime(int(rec.select_year), int(rec.select_month), 1)
            start_date = old_tz.localize(date_1).astimezone(new_tz)
            date_2 = datetime(int(rec.select_year), int(rec.select_month), 1) + relativedelta(months=1) #- relativedelta(days=1)
            end_date = old_tz.localize(date_2).astimezone(new_tz)
            for line in rec.valuation_adjustment_lines.filtered(lambda line: line.product_id):
                line.product_id.write({'cost_line_id' : line.id, 'standard_price' : line.pmac})
                stock_valuation = self.env['stock.valuation.layer'].search([('create_date','<=',end_date),('create_date','>=',start_date),('product_id','=',line.product_id.id)])
                for sv in stock_valuation:
                    sv.write({'unit_cost' : line.pmac, 'unit_cost_new' : line.pmac, 'value' : line.pmac * sv.quantity})
            rec.write({'state': 'done'})
            
    def get_valuation_lines_not_mixing(self, batch, tipe):
        lines_dict = {}
        for i in batch:
            data_mrp = i.mrp_line.filtered(lambda l: l.state == 'done')
            if i.product_id.id not in lines_dict:
                lines_dict[i.product_id.id] = {'uom' : i.bom_id.product_uom_id, 'mrp' : list(data_mrp.ids)}
            else:
                for x in data_mrp.ids:
                    lines_dict[i.product_id.id]['mrp'].append(x)
        return lines_dict
        
    def get_valuation_lines(self, batch, tipe):
        if tipe != 'Mixing':
            return self.get_valuation_lines_not_mixing(batch, tipe)
        else:
            lines_dict = {}
            for i in batch:
                data_mrp = i.mrp_line.filtered(lambda l: l.state == 'done')
                if i.product_id.id not in lines_dict:
                    lines_dict[i.product_id.id] = {'uom' : i.bom_id.product_uom_id,'mrp' : list(data_mrp.ids)}
                else:
                    for x in data_mrp.ids:
                        lines_dict[i.product_id.id]['mrp'].append(x)
            return lines_dict
    
    def get_stock_old(self, dict_data, k):
        date_1 = datetime(int(self.select_year), int(self.select_month), 1)
        date_from = date_1.strftime("%Y-%m-%d")
        date_to = (date_1 + relativedelta(days=1)).strftime("%Y-%m-%d")
        where_date_from = "move_line.date < '%s 00:00:00'" % (date_from)
        where_date_to = "move_line.date <= '%s 17:00:00'" % (date_to)
        where_product = "move_line.product_id = %s" % (k)
        where_location = "sl_from.name NOT LIKE 'External%' and sl_from.name NOT LIKE 'Internal%'"
        sql = """ 
        SELECT
            move_line.id,
            move_line.date,
            move_line.move_id,
            move_line.product_id,
            move_line.product_uom_id,
            move_line.location_id, 
            move_line.location_dest_id, 
            move_line.qty_done,
            case when %s then True else False end as is_initial
        FROM stock_move_line move_line
            join stock_location sl_from on move_line.location_id=sl_from.id 
            join stock_location sl_to on move_line.location_dest_id=sl_to.id 
        WHERE(sl_from.usage in ('production','inventory','customer') or sl_to.usage in ('production','inventory','customer')) and 
            move_line.location_id != move_line.location_dest_id and move_line.state = 'done' and %s and %s and %s and (move_line.not_adjust isnull or move_line.not_adjust=false)
    """ % (where_date_from, where_product, where_date_to, where_location)
        self._cr.execute(sql)
        data_revisi_qty = []
        for x in self._cr.dictfetchall():
            product = self.env['product.product'].browse(x['product_id'])
            prod_rev = self.env['revisi.onhand'].sudo().search([('product_id','=',product.id)])
            move = self.env['stock.move'].browse(x['move_id'])
            product_uom = self.env['uom.uom'].browse(x['product_uom_id'])
            location = self.env['stock.location'].browse(x['location_id'])
            location_dest = self.env['stock.location'].browse(x['location_dest_id'])
            qty = x['qty_done']
            if product_uom.id != product.uom_id.id:
                qty = product_uom._compute_quantity(qty, product.uom_id)
            if location_dest.usage in ('supplier','production','inventory','customer'):
                qty = -qty
                    
            if x['is_initial'] == True:
                if x['date'] <= datetime.strptime('2022-05-01 17:00:00', '%Y-%m-%d %H:%M:%S'):
                    if  prod_rev and prod_rev.id not in data_revisi_qty:
                        data_revisi_qty.append(prod_rev.id)
                        if prod_rev.product_id.id not in dict_data:
                            dict_data[prod_rev.product_id.id] = {'Awal' : [prod_rev.qty]}
                        else:
                            if 'Awal' not in dict_data[prod_rev.product_id.id]:
                                dict_data[prod_rev.product_id.id]['Awal'] = [prod_rev.qty]
                            else:
                                dict_data[prod_rev.product_id.id]['Awal'].append(prod_rev.qty)
                    else:
                        if product.id not in dict_data:
                            dict_data[product.id] = {'Awal' : [0]}
                        else:
                            if 'Awal' not in dict_data[product.id]:
                                dict_data[product.id]['Awal'] = [0]
                            else:
                                dict_data[product.id]['Awal'].append(0)
                else:
                    if product.id not in dict_data:
                        dict_data[product.id] = {'Awal' : [qty]}
                    else:
                        if 'Awal' not in dict_data[product.id]:
                            dict_data[product.id]['Awal'] = [qty]
                        else:
                            dict_data[product.id]['Awal'].append(qty)
        return dict_data

    def proses_compute_mrp_cost(self):
        batch_obj = self.env['batch.mrp.production']
        user_tz = self.env.user.tz
        old_tz = pytz.timezone('UTC')
        new_tz = pytz.timezone(user_tz)
        list_line = []
        for rec in self:
            date_1 = datetime(int(rec.select_year), int(rec.select_month), 1)
            start_date = old_tz.localize(date_1).astimezone(new_tz)
            date_start_up_Date = start_date.strftime("%Y-%m-%d 00:00:00")
            date_2 = datetime(int(rec.select_year), int(rec.select_month), 1) + relativedelta(months=1)
            end_date = old_tz.localize(date_2).astimezone(new_tz)
            end_date_up_Date = end_date.strftime("%Y-%m-%d 00:00:00")
            batch = batch_obj.search([('actual_complete_date','<=',end_date_up_Date),('actual_complete_date','>=',date_start_up_Date),('state','=','done'),('tipe','=',rec.tipe)])
            rec.write({'batch_ids': [(6, 0, batch.ids)]})
            all_val_line_values = rec.get_valuation_lines(batch, rec.tipe)
            for k, v in all_val_line_values.items():
                dict_data = {}
                if k not in dict_data:
                    dict_data[k] = {'Awal' : [0]}
                dict_data = self.get_stock_old(dict_data, k)
                quantity_last_stock = sum(dict_data[k]['Awal'])
                stock_value = self.env['product.product'].browse(k).standard_price
                lines = {
                    'name'                  : rec.name,
                    'product_id'            : k,
                    'Last_month_stock'      : quantity_last_stock,
                    'Last_month_cost'       : stock_value,
                    'mrp_ids'               : [(6, 0, v['mrp'])],
                }
                list_line += [(0, 0, lines)]
            rec.valuation_adjustment_lines = False
            rec.write({'valuation_adjustment_lines': list_line})
            rec.valuation_adjustment_lines.sudo().generate_fungsi_all()
            rec.valuation_adjustment_lines.sudo().generate_fungsi_end()
            rec._compute_total_valution()
    
    def proses_compute_mrp_cost_manual(self):
        for rec in self:
            for line in rec.valuation_adjustment_lines:
                line._generate_pmac()
                
    def compute_mrp_cost(self):
        for rec in self:
            if rec.last_stock_manual:
                rec.proses_compute_mrp_cost_manual()
            else:
                rec.proses_compute_mrp_cost()

    @api.model
    def create(self, vals):
        dt = date.today()
        period = self.env['account.period'].find(dt, self.env.company.id, 'mrp')
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('mrp.cost')
        res = super(MRPCost, self).create(vals)
        if not period:
            raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % dt))
        return res

    def write(self, values):
        dt = date.today()
        period = self.env['account.period'].find(dt, self.env.company.id, 'mrp')

        res = super(MRPCost, self).write(values)
        if not period:
            raise UserError(('There is no period defined for this date: %s.\nPlease go to Configuration/Periods.' % dt))
        return res    

    # def unlink(self):
    #     self.button_cancel()
    #     return super(MRPCost, self).unlink()


    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'done':
            return 'bmo_mrp_cost.mt_mrp_cost_open'
        return super(MRPCost, self)._track_subtype(init_values)


    def button_cancel(self):
        if any(cost.state == 'done' for cost in self):
            raise UserError(
                _('Validated landed costs cannot be cancelled, but you could create negative landed costs to reverse them'))
        return self.write({'state': 'cancel'})
    
class MRP_Cost_Line(models.Model):
    _name = 'mrp.cost.line'
    _description = 'MRP Cost Line'

    name = fields.Char('Description')
    cost_id = fields.Many2one(
        'mrp.cost', 'MRP Cost',
        required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    quantity = fields.Float(
        'Quantity', default=1.0, digits=0, required=True)
    price_unit = fields.Float('Cost', digits=dp.get_precision('Product Price'), required=True)
    account_id = fields.Many2one('account.account', 'Account', domain=[('deprecated', '=', False)])
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            self.quantity = 0.0
        self.name = self.product_id.name or ''
        self.price_unit = self.product_id.standard_price or 0.0
        self.account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id

class AdjustmentLines(models.Model):
    _name = 'mrp.valuation.adjustment.lines'
    _description = 'Valuation Adjustment Lines'
    
    name = fields.Char(
        'Description')
    cost_id = fields.Many2one(
        'mrp.cost', 'Landed Cost', ondelete='cascade', required=True)
    last_stock_manual = fields.Boolean("Manual", related='cost_id.last_stock_manual')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    lot_ids = fields.Many2many(
        'stock.production.lot', string='Lot Number')
    machine_usage_time = fields.Float(
        'Waktu Penggunaan mesin', digits=(12,4))
    allocation_ratio_origin = fields.Float(
        'Allocation Ratio Origin')
    allocation_ratio = fields.Float(
        'Allocation Ratio', default=0.0, digits=(12,4))
    allocation_fee = fields.Float(
        'Biaya Alokasi', digits=(12,4))
    consum_wip = fields.Float(
        "Consum wip", digits=(12,4))
    cost_wip = fields.Float(
        "Cost wip", digits=(12,4))
    biaya_wip = fields.Float(
        'Biaya WIP', digits=(12,4))
    production_result = fields.Float(
        'Hasil Produksi', digits=(12,4))
    cost_per_unit = fields.Float(
        'Cost Per Unit', digits=(12,4))
    Last_month_stock = fields.Float(
        'Stock Akhir Bulan lalu', digits=(12,4))
    Last_month_cost = fields.Float(
        'Cost Bulan lalu', digits=(12,4))
    pmac = fields.Float(
        'PMAC', digits=(12,4))
    result_pmac_prod = fields.Float(
        "PMAC*Total Produksi", digits=(12, 4))
    mrp_ids = fields.Many2many(
        'mrp.production', string='MRP')
    goods_qty = fields.Float(
        'Goods')
    reject_qty = fields.Float(
        'Reject')
    sampling_qty = fields.Float(
        'Sampling')
    stock_move_ids = fields.Many2many(
        'stock.move', string='MRP')
    
    def generate_fungsi_all(self):
        for rec in self:
            rec._generate_mrp()
            rec._generate_consum_wip()

    def generate_fungsi_end(self):
        for rec in self:
            rec._generate_ratio()
            rec._generate_pmac()

    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        return (factor * int(math.floor(val)), "{:0>2d}".format(int(round((val % 1) * 60))))

    def _generate_mrp(self):
        for rec in self:
            batch_mrp = self.env['batch.mrp.production'].browse(rec.cost_id.batch_ids.ids).filtered(lambda l: l.product_id.id == rec.product_id.id)
            machine_hour = 0
            for i in batch_mrp:
                a, b = rec.float_time_convert(i.machine_hour)
                time_str = f'{a}.{b}'
                machine_hour += float(time_str)
            rec.machine_usage_time = machine_hour
            rec.production_result = rec.goods_qty = sum(rec.mrp_ids.mapped('goods_qty'))
            rec.reject_qty = sum(rec.mrp_ids.mapped('reject_qty'))
            rec.sampling_qty = sum(rec.mrp_ids.mapped('sampling_qty'))
            rec.lot_ids = rec.mrp_ids.mapped('lot_producing_id').ids
            rec.stock_move_ids = rec.mrp_ids.mapped("move_raw_ids").filtered(lambda l: l.product_id.product_tmpl_id.bom_ids and l.state == 'done').ids
            rec.consum_wip = sum(rec.stock_move_ids.mapped('quantity_done'))
    
    def _generate_consum_wip(self):
        for rec in self:
            date_1 = datetime(int(rec.cost_id.select_year), int(rec.cost_id.select_month), 1)
            date_2 = datetime(int(rec.cost_id.select_year), int(rec.cost_id.select_month), 1) + relativedelta(months=1)
            product_wip = rec.stock_move_ids.mapped('product_id.id')[0] if rec.stock_move_ids else False
            stock_val_layer = self.env['stock.valuation.layer'].search([('product_id','=',product_wip),('create_date','>=',date_1),('create_date','<=',date_2)])
            cost_wip = 0
            if stock_val_layer:
                for layer in stock_val_layer :
                    if layer.unit_cost_new == 0.0 and cost_wip > 0:
                        layer.write({'unit_cost_new' : cost_wip})
                    cost_wip = layer.unit_cost_new
            else:
                cost_wip = self.env['product.product'].browse(product_wip).standard_price
            if cost_wip <= 0.0:
                cost_wip = self.env['product.product'].browse(product_wip).standard_price
            rec.cost_wip = cost_wip
            rec.biaya_wip = rec.consum_wip * rec.cost_wip

    def _generate_ratio(self):
        for rec in self:
            total_worker = rec.cost_id.machine_usage_time
            rec.allocation_ratio_origin = rec.machine_usage_time / total_worker
            rec.allocation_ratio = (rec.machine_usage_time / total_worker) * 100
            rec.allocation_fee = rec.allocation_ratio_origin * rec.cost_id.amount_total
            cost_per_unit = (rec.allocation_fee + (rec.consum_wip * rec.cost_wip)) / rec.production_result
            if rec.cost_id.tipe == 'Mixing':
                cost_per_unit = rec.allocation_fee / rec.production_result
            rec.cost_per_unit = cost_per_unit

    def _generate_pmac(self):
        for line in self:
            if line.cost_id.tipe == 'Mixing':
                pmac = (
                    (line.allocation_fee + (line.Last_month_stock * line.Last_month_cost)) / (line.production_result + line.Last_month_stock))
            else:
                pmac = (((line.Last_month_stock * line.Last_month_cost) + line.biaya_wip) +
                        line.allocation_fee) / (line.production_result + line.Last_month_stock)
            line.write(
                {'pmac': pmac, 'result_pmac_prod': pmac * line.production_result})

class StockValuationLayer(models.Model):
    """Stock Valuation Layer"""

    _inherit = 'stock.valuation.layer'

    stock_mrp_cost_id = fields.Many2one('mrp.cost', 'Landed Cost')

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    mrp_cost_id = fields.Many2one(
        comodel_name='mrp.cost', string='MRP Cost', copy=False)
