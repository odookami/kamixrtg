from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from datetime import date, datetime, timedelta, time
import datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.bmo_mrp.models.product import state_tipe
from odoo.tools import float_compare, float_round, float_is_zero, format_datetime
from odoo.osv import expression
import logging
_logger = logging.getLogger(__name__)

class Mrp_OKP(models.Model):
    _name = "mrp.okp"
    _description = 'OKP'
    
    name = fields.Char('Name', default=lambda self: self.env['ir.sequence'].next_by_code('okp.sequence'))
    state = fields.Selection(string='Status', selection=[('draft', 'Draft'), ('Close', 'Close'),], default='draft')
    batch_mo_line = fields.One2many(
        comodel_name='batch.mrp.production', inverse_name='okp_id', string='Batch mrp')
    mo_ids = fields.One2many(
        comodel_name='mrp.production', inverse_name='okp_id', string='MO')

class BatchMrpProduction(models.Model):
    _name = 'batch.mrp.production'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Batch mrp production"
    _order = "okp_id desc"
    
    @api.model
    def _get_default_picking_type(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', '=', company_id),
        ], limit=1).id
    
    @api.model
    def _get_default_location_src_id(self):
        location = False
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        if self.env.context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_src_id
        if not location:
            location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        return location and location.id or False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_dest_id
        if not location:
            location = self.env['stock.warehouse'].search([('company_id', '=', company_id)], limit=1).lot_stock_id
        return location and location.id or False
    
    @api.model
    def _get_default_date_planned_finished(self):
        if self.env.context.get('default_date_planned_start'):
            return fields.Datetime.to_datetime(self.env.context.get('default_date_planned_start')) + datetime.timedelta(hours=1)
        return datetime.datetime.now() + datetime.timedelta(hours=1)

    @api.model
    def _get_default_date_planned_start(self):
        if self.env.context.get('default_date_deadline'):
            return fields.Datetime.to_datetime(self.env.context.get('default_date_deadline'))
        return datetime.datetime.now()
    
    def _default_start_datetime(self):
        return datetime.datetime.now()
    
    name = fields.Char(
        'Nomor Urut BO', tracking=True)
    number_bo = fields.Char(
        "Nomor BO", tracking=True) 
    bo_fee = fields.Char("BO FEE")
    okp_id = fields.Many2one(
        'mrp.okp', 'No. OKP', tracking=True)
    reference = fields.Char(
        'NO. OKP Ref', tracking=True)
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company, index=True, required=True, tracking=True)
    product_id = fields.Many2one(
        'product.product', 'Product', domain="[('id', 'in', allowed_product_ids)]", required=True, check_company=True, tracking=True)
    allowed_product_ids = fields.Many2many('product.product', compute='_compute_allowed_product_ids')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', related='product_id.product_tmpl_id', tracking=True)
    bom_id = fields.Many2one(
        'mrp.bom', 'Formula',
        readonly=True, states={'draft': [('readonly', False)]},
        domain="""[
        '&',
            '|',
                ('company_id', '=', False),
                ('company_id', '=', company_id),
            '&',
                '|',
                    ('product_id','=',product_id),
                    '&',
                        ('product_tmpl_id.product_variant_ids','=',product_id),
                        ('product_id','=',False),
        ('tipe', '=', tipe)]""",
        check_company=True,
        help="Bill of Materials allow you to define the list of required components to make a finished product.")
    version = fields.Integer('Version', related="bom_id.version")
    date_okp = fields.Date(
        'Tgl. OKP', default=_default_start_datetime, tracking=True)
    tipe = fields.Selection(
        state_tipe, string='Type OKP', tracking=True)
    batch_mo_id = fields.Many2one(
        'batch.mrp.production', 'Batch mrp')
    batch_proses = fields.Float(
        string='Batch Proses', tracking=True)
    goods_qty = fields.Float(
        'Goods', default=0.0, compute='_compute_qty_production', store=True)
    reject_qty = fields.Float(
        'Reject', default=0.0, compute='_compute_qty_production', store=True)
    sampling_qty = fields.Float(
        'Sampling QC Internal', default=0.0, compute='_compute_qty_production', store=True)
    sampling_ex_qty = fields.Float(
        'Sampling QC External', default=0.0, compute='_compute_qty_production', store=True)
    sampling_marketing_qty = fields.Integer(
        compute='_compute_qty_production', string='Sampling Marketing', store=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        domain="[('code', '=', 'mrp_operation'), ('company_id', '=', company_id)]",
        default=_get_default_picking_type, required=True, check_company=True)
    location_src_id = fields.Many2one(
        'stock.location', 'Components Location',
        default=_get_default_location_src_id,
        readonly=True, required=True,
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}, check_company=True,
        help="Location where the system will look for components.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location',
        default=_get_default_location_dest_id,
        readonly=True, required=True,
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        states={'draft': [('readonly', False)]}, check_company=True,
        help="Location where the system will stock the finished products.")
    date_planned_start = fields.Datetime(
        'Scheduled Date', copy=False, default=_get_default_date_planned_start,
        help="Date at which you plan to start the production.",
        index=True, required=True)
    date_planned_finished = fields.Datetime(
        'Scheduled End Date',
        default=_get_default_date_planned_finished,
        help="Date at which you plan to finish the production.",
        copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('done', 'Close'),
        ('cancel', 'Cancelled')], default='draft', string='State', copy=False, index=True, readonly=True, tracking=True,)
    mrp_line = fields.One2many(
        'mrp.production', 'bache_id', string='MRP Line')
    group_components_line = fields.One2many(
        'group.components.mrp', 'bache_id', string='Group Components')
    move_raw_ids = fields.One2many(
        'stock.move', 'raw_material_bache_id', 'Components', copy=False)
    workorder_duration = fields.Float(
        'Workorder Duration', compute='_compute_qty_production', store=True)
    cek_state_mo = fields.Boolean('Cek Status MO', compute='_compute_mrp_line')
    close_bo = fields.Boolean(
        'Close BO', compute='_compute_bo', default=False, store=True)
    planned_start = fields.Datetime(
        "Planned Start")
    planned_completion = fields.Datetime(
        "Planned Completion")
    required_completion = fields.Datetime(
        "Required Completion")
    actual_date = fields.Datetime(
        "Actual Start Date")
    actual_complete_date = fields.Datetime(
        "Actual Complete Date")
    production_time = fields.Float(
        "Production time", compute="_compute_production_time")
    breaktime_date = fields.Datetime(
        "Start Breaktime")
    breaktime_end_date = fields.Datetime(
        "Complete Breaktime")
    # breaktime = fields.Float(
    #     "Breaktime", compute="_compute_production_time")
    breaktime = fields.Float(
        "Breaktime")
    machine_hour = fields.Float(
        "Machine Time", compute="_compute_production_time", store=True)
    actual_closing = fields.Datetime(
        "Actual Closing")
    
    @api.constrains('okp_id','tipe')
    def _check_tipe(self):
        for rec in self:
            cek_data = rec.search([('okp_id','=',rec.okp_id.id),('tipe','=',rec.tipe),('id','!=',rec.id),('state','!=','cancel')])
            if cek_data:
                raise UserError(_(f'No OKP {rec.okp_id.name} Penah di buat {rec.tipe}'))

    @api.depends('mrp_line')
    def _compute_qty_production(self):
        for rec in self:
            rec.goods_qty = sum([x.goods_qty for x in rec.mrp_line if x.state not in ('cancel','draft')])
            rec.reject_qty = sum([x.reject_qty for x in rec.mrp_line if x.state not in ('cancel','draft')])
            rec.sampling_qty = sum([x.sampling_qty for x in rec.mrp_line if x.state not in ('cancel','draft')])
            rec.sampling_ex_qty = sum([x.sampling_ex_qty for x in rec.mrp_line if x.state not in ('cancel','draft')])
            rec.sampling_marketing_qty = sum([x.sampling_marketing_qty for x in rec.mrp_line if x.state not in ('cancel','draft')])
    
    def generate_ulang_hasil(self):
        for rec in self.search([]):
            rec.goods_qty = sum(
                [x.goods_qty for x in rec.mrp_line if x.state not in ('cancel', 'draft')])
            rec.reject_qty = sum(
                [x.reject_qty for x in rec.mrp_line if x.state not in ('cancel', 'draft')])
            rec.sampling_qty = sum(
                [x.sampling_qty for x in rec.mrp_line if x.state not in ('cancel', 'draft')])
            rec.sampling_ex_qty = sum(
                [x.sampling_ex_qty for x in rec.mrp_line if x.state not in ('cancel', 'draft')])
            rec.sampling_marketing_qty = sum(
                [x.sampling_marketing_qty for x in rec.mrp_line if x.state not in ('cancel', 'draft')])

    # @api.depends('actual_date', 'actual_complete_date','breaktime_date','breaktime_end_date')
    @api.depends('actual_date', 'actual_complete_date','breaktime')
    def _compute_production_time(self):
        for rec in self:
            total_hour = 0
            # breaktime = 0
            if rec.actual_date and rec.actual_complete_date:
                time_pro = rec.actual_date - rec.actual_complete_date
                total_hour = abs(float(time_pro.days) * 24 + (float(time_pro.seconds) / 3600))
            else:
                total_hour = 0
            rec.production_time = total_hour
            rec.machine_hour = total_hour - rec.breaktime

    @api.depends('batch_mo_id')
    def _compute_bo(self):
        for rec in self:
            if rec.batch_mo_id and rec.batch_mo_id.state == 'done' and rec.state == 'done':
                rec.batch_mo_id.close_bo = True
            else:
                rec.close_bo = False
    
    def action_cancel(self):
        for o in self:
            for mrp in o.mrp_line:
                if mrp.state not in ('draft','cancel'):
                    raise UserError(_("Hanya bisa cancel Mo dengan status draft,cancel"))
                mrp.write({'state' : 'cancel'})
            o.write({'state' : 'cancel'})

    @api.depends('mrp_line','mrp_line.state')
    def _compute_mrp_line(self):
        for rec in self:
            mrp = rec.mrp_line.search([('bache_id','=',rec.id),('state','in',['draft','confirmed','progress'])])
            if not mrp:
                rec.write({'state' : 'done', 'cek_state_mo' : True})
                rec.okp_id.write({'state' : 'Close'})
                rec._compute_bo()
            else:
                rec.update({'cek_state_mo' : False})    
    
    @api.depends('product_id', 'bom_id', 'company_id')
    def _compute_allowed_product_ids(self):
        for production in self:
            product_domain = [
                ('type', 'in', ['product', 'consu']),
                '|',
                    ('company_id', '=', False),
                    ('company_id', '=', production.company_id.id)
            ]
            if production.bom_id:
                if production.bom_id.product_id:
                    product_domain += [('id', '=', production.bom_id.product_id.id)]
                else:
                    product_domain += [('id', 'in', production.bom_id.product_tmpl_id.product_variant_ids.ids)]
            production.allowed_product_ids = self.env['product.product'].search(product_domain)
    
    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        if not self.product_id:
            self.bom_id = False
        elif not self.bom_id or self.bom_id.product_tmpl_id != self.product_tmpl_id or (self.bom_id.product_id and self.bom_id.product_id != self.product_id):
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id, bom_type='normal')
            if bom:
                self.bom_id = bom.id
            else:
                self.bom_id = False
    
    @api.onchange('batch_mo_id')
    def _onchange_batch_mo_id(self):
        for rec in self:
            if rec.batch_mo_id:
                rec.batch_proses = rec.batch_mo_id.batch_proses
                
    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        if not self.product_id and self.bom_id:
            self.product_id = self.bom_id.product_id or self.bom_id.product_tmpl_id.product_variant_ids[0]
        self.picking_type_id = self.bom_id.picking_type_id or self.picking_type_id
    
     
    def _compute_group_components(self):
        list_line = []
        lines_dict = {}
        if self.move_raw_ids:
            for move in self.move_raw_ids:
                if move.product_id.id not in lines_dict:
                    lines_dict[move.product_id.id] = {move.product_uom.id:[move.product_uom_qty]}
                else:
                    if move.product_uom.id not in lines_dict[move.product_id.id]:
                        lines_dict[move.product_id.id][move.product_uom.id] = [move.product_uom_qty]
                    else:
                        if move.product_uom.id in lines_dict[move.product_id.id]:
                            if move.product_uom.id not in lines_dict[move.product_id.id][move.product_uom.id]:
                                lines_dict[move.product_id.id][move.product_uom.id].append(move.product_uom_qty)
            for k, v in lines_dict.items():
                product = self.env['product.product'].browse(k)
                for x, y in v.items():
                    uom = self.env['uom.uom'].browse(x)
                    qty = sum(y)
                    lines = {
                        'product_uom_id': uom.id,
                        'qty': qty,
                        'product_id': product.id,
                    }
                    list_line += [(0, 0, lines)]
            self.write({'group_components_line': list_line})

        
    def create_mo(self):
        for rec in self:
            if rec.batch_proses <= 0:
                raise UserError(_('Batch Proses Tidak Boleh 0'))
            if not rec.planned_start:
                raise UserError(_('Planned Start Tidak Boleh Kosong'))
            number = 0
            if rec.tipe != 'Mixing':
                number += 1
                value = {
                    'bache_id'          : rec.id,
                    'number_ref'        : f'{rec.name}{number}',
                    'okp_id'            : rec.okp_id.id,
                    'tipe'              : rec.tipe,
                    'product_id'        : rec.product_id.id,
                    'bom_id'            : rec.bom_id.id,
                    'product_qty'       : rec.batch_proses,
                    'product_uom_id'    : rec.bom_id.product_uom_id.id,
                    'picking_type_id'   : rec.picking_type_id.id,
                    'location_src_id'   : rec.location_src_id.id,
                    'location_dest_id'  : rec.location_dest_id.id,
                    'origin'            : rec.okp_id.name,
                    'date_planned_start': rec.planned_start,
                }
                
                production = self.env['mrp.production'].create(value)
                production._onchange_move_raw()
                production._onchange_move_finished()
                production._compute_product_uom_qty()
                production.action_create_nbs()
                # production._create_workorder()
            else:
                for i in range(1, int(rec.batch_proses)+1):
                    number += 1
                    value = {
                        'bache_id'          : rec.id,
                        'number_ref'        : f'{rec.name}{number}',
                        'okp_id'            : rec.okp_id.id,
                        'tipe'              : rec.tipe,
                        'product_id'        : rec.product_id.id,
                        'bom_id'            : rec.bom_id.id,
                        'product_qty'       : 1,
                        'product_uom_id'    : rec.bom_id.product_uom_id.id,
                        'picking_type_id'   : rec.picking_type_id.id,
                        'location_src_id'   : rec.location_src_id.id,
                        'location_dest_id'  : rec.location_dest_id.id,
                        'origin'            : rec.okp_id.name,
                        'date_planned_start': rec.planned_start,
                    }
                    
                    production = self.env['mrp.production'].create(value)
                    production._onchange_move_raw()
                    production._onchange_move_finished()
                    production._compute_product_uom_qty()
                    production.action_create_nbs()
                    # production._create_workorder()

    def action_closes_mrp(self):
        for rec in self:
            rec._compute_qty_production()
            if not rec.actual_date or not rec.actual_complete_date:
                raise UserError(_("Mohon isi field Actual Start Date and Actual Complete Date"))
            if not rec.actual_closing and rec.state in ['progress','done']:
                rec.write({'actual_closing' : datetime.datetime.now(), 'state' : 'done'})
                for line in rec.mrp_line:
                    if line.state not in ('cancel','done'):
                        raise UserError(_("Mohon Mohon Selesaikan Proeses atau Cancel"))
                    line.action_closes_mrp()
                    if not line.okp_id:
                        line.wrtie({'okp_id' : rec.okp_id.id})
                    for move in line.move_raw_ids:
                        if not move.raw_material_bache_id:
                            move.write({'raw_material_bache_id' : rec.id})
                            rec._compute_group_components()

    def action_confirmed(self):
        self.ensure_one()
        for rec in self:
            rec.create_mo()
            rec._compute_group_components()
            rec.state = 'progress'
    
    def update_bo(self):
        for rec in self:
            name_bo = rec.name
            for mrp in rec.mrp_line:
                name_mrp = mrp.name.split(" ")
                number_1 = mrp.number_ref[:1]
                number_2 = mrp.number_ref[1:2]
                mrp.name = f'[{name_bo}{number_2}] {name_mrp[1]}'
                mrp.number_ref = f'{name_bo}{number_2}'
                for x in mrp.number_proses_line:
                    number_11 = x.number[:1]
                    number_22 = x.number[1:2]
                    x.number = f'{name_bo}{number_22}'

    # ----------------------------------------------------------------------------
    # ORM Overrides
    # ----------------------------------------------------------------------------

    @api.model
    def create(self, vals):
        batch_obj = self.env['batch.mrp.production']
        tipe = vals['tipe']
        if tipe == 'Mixing':
            vals['okp_id'] = self.env['mrp.okp'].create({'state' : 'draft'}).id
        if tipe != 'Mixing' and not vals['batch_mo_id']:
            if tipe == 'Filling':
                cek_batch = batch_obj.search([('okp_id','=',vals['okp_id']),('tipe','=','Filling'),('state','!=','cancel')])
                batch = batch_obj.search([('okp_id','=',vals['okp_id']),('tipe','=','Mixing'),('state','!=','cancel')])
                if cek_batch:
                    raise UserError(_(f'"{tipe}" Pernah di buat')) 
                if not batch:
                    raise UserError(_(f'Mohon Buat Dulu "Mixing"')) 
            else:
                cek_batch = batch_obj.search([('okp_id','=',vals['okp_id']),('tipe','=','Banded'),('state','!=','cancel')])
                batch = batch_obj.search([('okp_id','=',vals['okp_id']),('tipe','=','Filling'),('state','!=','cancel')])
                if cek_batch:
                    raise UserError(_(f'{tipe} Pernah di buat')) 
                if not batch:
                    raise UserError(_(f'Mohon Buat Dulu "Filling"')) 
            vals['batch_mo_id'] = batch.id
            vals['batch_proses'] = batch.batch_proses
            vals['name'] = batch.name
        return super(BatchMrpProduction, self).create(vals)
    
    def unlink(self):
        for rec in self:
            if rec.mrp_line:
                raise UserError(_('Cannot delete a Batch mrp.'))
        return super(BatchMrpProduction, self).unlink()


    def name_get(self):
        res = []
        for rec in self:
            name = '[' + str(rec.okp_id.name) + '] ' + ' ' + rec.tipe + ' ' + str(rec.name)
            res.append((rec.id, name))
        return res
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|','|', ('name', 'ilike', name), ('reference', 'ilike', name),('okp_id.name', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    state = fields.Selection(selection_add=[('approved', 'Approved'),('done',)])
    okp_id = fields.Many2one(
        'mrp.okp', 'OKP', tracking=True)
    tipe = fields.Selection(
        state_tipe, string='Type', tracking=True)
    bache_id = fields.Many2one(
        comodel_name='batch.mrp.production', string='Batch MRP', required=True, ondelete='cascade', tracking=True)
    suggest_qty = fields.Float(
        "Suggest Qty", compute="_qty_suggest_prod")
    sugges_uom_id = fields.Many2one(
        'uom.uom', string="Unit of Measure", related="product_id.uom_id")
    goods_qty = fields.Float(
        'Goods', default=0.0, compute="_compute_real_qty", tracking=True)
    reject_qty = fields.Float(
        'Reject', default=0.0, compute='_compute_scrap_data', store=True, tracking=True)
    sampling_qty = fields.Float(
        'Sampling QC Internal', default=0.0, compute='_compute_scrap_data', store=True, tracking=True)
    sampling_ex_qty = fields.Float(
        'Sampling QC External', default=0.0, compute='_compute_scrap_data', store=True, tracking=True)
    sampling_marketing_qty = fields.Float(
        'Sampling Marketing', compute='_compute_scrap_data', store=True, default=0.0, tracking=True)
    sampling_count = fields.Integer(
        compute='_compute_sampling_move_count', string='Sampling Move', tracking=True)
    sampling_marketing_count = fields.Integer(
        compute='_compute_sampling_marketing_move_count', string='Sampling Marketing Move', tracking=True)
    number_ref = fields.Char("Nomor Batch Order")
    shift = fields.Selection([
        ('1', 'I'),('2', 'II'),('3', 'III')], string='Shift', tracking=True
    )
    actual_closing = fields.Datetime(
        "Actual Closing", tracking=True)
    actual_date = fields.Datetime(
        "Actual Start Date", tracking=True)
    actual_complete_date = fields.Datetime(
        "Actual Complete Date", tracking=True)
    date_done = fields.Date(
        "Date Done"
    )
    number_proses_line = fields.One2many(
        'number.batch.proses', 'mo_id', string='Number Batch Proses')
    active = fields.Boolean('Active', default=True)
    unbuild = fields.Boolean("Unbuild", default=False)

    def set_qty_done(self):
        self.ensure_one()
        for line in self.move_raw_ids:
            if line.move_line_ids:
                for move in line.move_line_ids:
                    move.write({'qty_done' : move.product_uom_qty})


    def _qty_suggest_prod(self):
        for rec in self:
            if rec.tipe != "Mixing":
                rec.suggest_qty = rec.bom_id.product_uom_id._compute_quantity(rec.bache_id.batch_proses, rec.product_id.uom_id)
            else:
                rec.suggest_qty = rec.bom_id.product_uom_id._compute_quantity(1, rec.product_id.uom_id)

    def _compute_scrap_move_count(self):
        data = self.env['stock.scrap'].read_group([('production_id', 'in', self.ids),('tipe','=','scrap')], ['production_id'], ['production_id'])
        count_data = dict((item['production_id'][0], item['production_id_count']) for item in data)
        for production in self:
            production.scrap_count = count_data.get(production.id, 0)
    
    def _compute_sampling_move_count(self):
        data = self.env['stock.scrap'].read_group([('production_id', 'in', self.ids),('tipe','=','sampling')], ['production_id'], ['production_id'])
        count_data = dict((item['production_id'][0], item['production_id_count']) for item in data)
        for production in self:
            production.sampling_count = count_data.get(production.id, 0)
    
    def _compute_sampling_marketing_move_count(self):
        data = self.env['stock.scrap'].read_group([('production_id', 'in', self.ids),('tipe','=','sampling_marketing')], ['production_id'], ['production_id'])
        count_data = dict((item['production_id'][0], item['production_id_count']) for item in data)
        for production in self:
            production.sampling_marketing_count = count_data.get(production.id, 0)

    def action_closes_mrp(self):
        for rec in self:
            if not rec.actual_closing and rec.state == 'done':
                rec.actual_closing = datetime.datetime.now()

    @api.depends('qty_producing','goods_qty','reject_qty','sampling_qty','sampling_marketing_qty','sampling_ex_qty')
    def _compute_real_qty(self):
        for rec in self:
            rec.goods_qty = rec.product_uom_id._compute_quantity(rec.qty_producing, rec.product_id.uom_id) - rec.reject_qty - rec.sampling_qty - rec.sampling_marketing_qty - rec.sampling_ex_qty

    @api.depends('scrap_ids','scrap_ids.scrap_qty','scrap_ids.state')
    def _compute_scrap_data(self):
        for rec in self:
            scrap_obj = self.env['stock.scrap']
            sampling_int = self.env.ref('bmo_inventory.master_type_1').id
            sampling_ext = self.env.ref('bmo_inventory.master_type_2').id
            rec.reject_qty = sum([x.product_uom_id._compute_quantity(x.scrap_qty, x.product_id.uom_id) for x in scrap_obj.search([
                ('production_id', '=', rec.id),('tipe', '=', 'scrap'),('state','=','done')])])
            rec.sampling_qty = sum([x.product_uom_id._compute_quantity(x.scrap_qty, x.product_id.uom_id) for x in scrap_obj.search([
                ('production_id', '=', rec.id),('tipe', '=', 'sampling'),('state','=','done'),('master_type_id','=',sampling_int)])])
            rec.sampling_ex_qty = sum([x.product_uom_id._compute_quantity(x.scrap_qty, x.product_id.uom_id) for x in scrap_obj.search([
                ('production_id', '=', rec.id),('tipe', '=', 'sampling'),('state','=','done'),('master_type_id','=',sampling_ext)])])
            rec.sampling_marketing_qty = sum([x.product_uom_id._compute_quantity(x.scrap_qty, x.product_id.uom_id) for x in scrap_obj.search([
                ('production_id', '=', rec.id),('tipe', '=', 'sampling_marketing'),('state','=','done'),('master_type_id','=',sampling_ext)])])

    def action_see_move_scrap(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        action['domain'] = [('production_id', '=', self.id),('tipe', '=', 'scrap')]
        action['context'] = dict(self._context, default_origin=self.name)
        return action

    def button_scrap(self):
        # if self.actual_closing:
        #     raise UserError(_("This entry has been closed"))
        scrap_location_id = self.env['res.company']._company_default_get('res.config.settings').scrap_location_id
        if not scrap_location_id:
            raise UserError(_("Mohon Tetapkan Lokasi Scrap 'Configuration => Setting'"))
        self.ensure_one()
        reject = self.env.ref('bmo_inventory.master_type_3')
        return {
            'name': _('Scrap'),
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_production_id': self.id,
                        'default_tipe'  : 'scrap',
                        'default_lot_id' : self.lot_producing_id.id,
                        'default_product_id'  : self.product_id.id,
                        'default_master_type_id' : reject.id or False,
                        'product_ids': (self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids,
                        'default_company_id': self.company_id.id,
                        'default_scrap_location_id' : reject.location_id.id
                        },
            'target': 'new',
        }
    
    def action_see_move_sampling(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        action['domain'] = [('production_id', '=', self.id),('tipe', '=', 'sampling')]
        action['context'] = dict(self._context, default_origin=self.name)
        return action

    def button_sampling(self):
        # if self.actual_closing:
        #     raise UserError(_("This entry has been closed"))
        sampling_location_id = self.env['res.company']._company_default_get('res.config.settings').sampling_location_id
        if not sampling_location_id:
            raise UserError(_("Mohon Tetapkan Lokasi Sampling 'Configuration => Setting'"))
        self.ensure_one()
        return {
            'name': _('Sampling'),
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_production_id': self.id,
                        'default_tipe'  : 'sampling',
                        'default_lot_id' : self.lot_producing_id.id,
                        'default_product_id'  : self.product_id.id,
                        'product_ids': (self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids,
                        'default_company_id': self.company_id.id,
                        'default_scrap_location_id' : sampling_location_id.id
                        },
            'target': 'new',
        }
    
    def action_see_move_sampling_marketing(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_stock_scrap")
        action['domain'] = [('production_id', '=', self.id),('tipe', '=', 'sampling_marketing')]
        action['context'] = dict(self._context, default_origin=self.name)
        return action

    def button_sampling_marketing(self):
        if self.actual_closing:
            raise UserError(_("This entry has been closed"))
        if self.tipe == 'Mixing':
            raise UserError(_("Sampe Marketing Hanya Bisa di Lakukan di Type OKP Selain 'Mixing'"))
        sampling_marketing_location_id = self.env['res.company']._company_default_get('res.config.settings').sampling_marketing_location_id
        if not sampling_marketing_location_id:
            raise UserError(_("Mohon Tetapkan Lokasi Sampling Marketing 'Configuration => Setting'"))
        self.ensure_one()
        sampling_marketing = self.env.ref('bmo_inventory.master_type_4')
        return {
            'name': _('Sampling Marketing'),
            'view_mode': 'form',
            'res_model': 'stock.scrap',
            'view_id': self.env.ref('stock.stock_scrap_form_view2').id,
            'type': 'ir.actions.act_window',
            'context': {'default_production_id': self.id,
                        'default_tipe'  : 'sampling_marketing',
                        'default_lot_id' : self.lot_producing_id.id,
                        'default_product_id'  : self.product_id.id,
                        'default_master_type_id' : sampling_marketing.id or False,
                        'product_ids': (self.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel')) | self.move_finished_ids.filtered(lambda x: x.state == 'done')).mapped('product_id').ids,
                        'default_company_id': self.company_id.id,
                        'default_scrap_location_id' : sampling_marketing.location_id.id
                        },
            'target': 'new',
        }

    def action_generate_serial(self):
        self.ensure_one()
        self.lot_producing_id = self.env['stock.production.lot'].create({
            'product_id': self.product_id.id,
            'company_id': self.company_id.id,
            'bache_id'  : self.bache_id.id,
            'mo_id'     : self.id,
        })
        if self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids:
            self.move_finished_ids.filtered(lambda m: m.product_id == self.product_id).move_line_ids.lot_id = self.lot_producing_id
        if self.product_id.tracking == 'serial':
            self._set_qty_producing()

    def button_unbuild(self):
        if self.unbuild:
            raise UserError(_("Dokumen %s Pernah Di Unbuild") %s(self.name))
        return super(MrpProduction, self).button_unbuild()
    
    def _pre_button_mark_done_new(self):
        productions_to_immediate = self._check_immediate()
        if productions_to_immediate:
            return productions_to_immediate._action_generate_immediate_wizard()

        for production in self:
            if float_is_zero(production.qty_producing, precision_rounding=production.product_uom_id.rounding):
                raise UserError(_('The quantity to produce must be positive!'))

        consumption_issues = self._get_consumption_issues()
        if consumption_issues:
            return self._action_generate_consumption_wizard(consumption_issues)

        quantity_issues = self._get_quantity_produced_issues()
        return True

    def action_create_nbs(self):
        for o in self:
            if o.bache_id:
                name = o.bache_id.name
                batch_proses = o.bache_id.batch_proses
                number = 0
                for x in range(int(batch_proses)):
                    number += 1
                    self.env['number.batch.proses'].create({
                        'number' : f'{name}{number}',
                        'okp_id' : o.okp_id.id,
                        'tipe'   : o.tipe,
                        'mo_id'  : o.id,
                    })

    def update_ed_lot(self):
        for rec in self:
            if rec.okp_id.id != rec.lot_producing_id.okp_id.id:
                if rec.tipe == 'Mixing':
                    ed = rec.actual_complete_date + relativedelta(months=self.product_id.expiration_month)
                    rec.lot_producing_id.sudo().write({'expiration_date' : ed, 'okp_id' : rec.okp_id.id})
                else:
                    mrp_mixing = self.env['mrp.production'].search([('tipe','=', 'Mixing'),('okp_id','=', rec.okp_id.id),('state','=','done')], limit=1)
                    rec.lot_producing_id.expiration_date = mrp_mixing.lot_producing_id.expiration_date

    def button_mark_done(self):
        picking_obj = self.env['stock.picking']
        for rec in self:
            rec.bache_id._compute_qty_production()
            rec.bache_id._compute_mrp_line()
            if not rec.shift or not rec.actual_date or not rec.actual_complete_date:
                raise UserError(_('Mohon isi Field "Shift" or "Actual Start Date" or "Actual Complete Date"'))
            if rec.state in ['confirmed','progress','to_close']:
                rec._button_mark_done_sanity_checks()
                res = rec._pre_button_mark_done_new()
                if res is not True:
                    return res
                rec.write({'state' : 'approved'})
                if rec.move_finished_ids:
                    for x in rec.move_finished_ids:
                        if x.product_uom.id != rec.product_uom_id.id:
                            x.product_uom = rec.product_uom_id.id
            else:
                result_res = super(MrpProduction, self).button_mark_done()
                mo = self.search([('tipe','=',rec.tipe),('bache_id','=',rec.bache_id.id),('lot_producing_id','=',False)])
                if mo:
                    for m in mo:
                        m.write({'lot_producing_id' : rec.lot_producing_id.id})
                rec.date_done = date.today()
                rec.update_ed_lot()
                return result_res
    
    def action_confirm(self):
        for rec in self:
            rec.move_finished_ids.unlink()
            if rec.product_id.uom_id.id != rec.product_uom_id.id:
                raise UserError(_('Mohon Ganti UoM terlebih dulu'))
            if rec.suggest_qty != rec.product_qty:
                raise UserError(_('Qty Sugges Harus sama dengan qty produksi'))
            rec._onchange_move_finished()
        return super(MrpProduction, self).action_confirm()

    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
        res = super(MrpProduction, self)._get_move_raw_values(product_id, product_uom_qty, product_uom, operation_id, bom_line)
        res['raw_material_bache_id'] = self.bache_id.id
        return res
    
    @api.depends(
        'move_raw_ids.state', 'move_raw_ids.quantity_done', 'move_finished_ids.state',
        'workorder_ids', 'workorder_ids.state', 'product_qty', 'qty_producing')
    def _compute_state(self):
        for production in self:
            if production.state == 'done':
                for move in production.move_raw_ids:
                    if move.product_uom_qty == 0 and move.quantity_done == 0:
                        move.write({'state' : 'draft'})
                        move.sudo().unlink()
        return super(MrpProduction, self)._compute_state()


    @api.model
    def create(self, values):
        res = super(MrpProduction, self).create(values)
        if res.name:
            res.name = f'[{res.number_ref}] {res.okp_id.name}/{res.name}'
        return res
    
    def name_get(self):
        res = []
        for rec in self:
            name = '[' + str(rec.number_ref) + '] ' + ' ' + str(rec.okp_id.name) + ' - ' + str(rec.tipe)
            res.append((rec.id, name))
        return res

class Number_Batch_proses(models.Model):
    _name = 'number.batch.proses'
    _description = "Number Batch Proses"
    
    number = fields.Char("Number")
    okp_id = fields.Many2one(
        'mrp.okp', 'OKP')
    tipe = fields.Selection(
        state_tipe, string='Type')
    mo_id = fields.Many2one(
        comodel_name='mrp.production', string='MO', required=True, ondelete='cascade')
    
    def name_get(self):
        res = []
        for rec in self:
            name = '[' + str(rec.number) + '] ' + ' ' + str(rec.okp_id.name) + ' - ' + str(rec.tipe)
            res.append((rec.id, name))
        return res

class GroupComponents(models.Model):
    _name= "group.components.mrp"
    _description = "Group Components MRP"
    _rec_name = "product_id"

    bache_id = fields.Many2one(
        comodel_name='batch.mrp.production', string='Batch MRP', required=True, ondelete='cascade')
    product_id = fields.Many2one("product.product","product")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom_id = fields.Many2one(
        'uom.uom', 'Unit of Measure', required=True, domain="[('category_id', '=', product_uom_category_id)]")
    qty = fields.Float("qty")

class StockMove(models.Model):
    _inherit = 'stock.move'

    raw_material_bache_id = fields.Many2one(
        'batch.mrp.production', 'Production Order for components', check_company=True, index=True)

    def write(self, vals):
        for move in self:
            production = move.production_id or move.raw_material_production_id
            if production and production.actual_complete_date:
                vals['date'] = production.actual_complete_date
        return super(StockMove, self).write(vals)
    

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def update_stock_date(self):
        for rec in self:
            for move_line in self:
                production = move_line.move_id.production_id or move_line.move_id.raw_material_production_id
                if production and move_line.state not in ('draft','cancel') and production.actual_complete_date:
                    move_line.write({'date' : production.actual_complete_date})
                    move_line.move_id.write({'date' : production.actual_complete_date})
                    src_svl = self.env['stock.valuation.layer'].search([('stock_move_id','=',move_line.move_id.id)])
                    for svl in src_svl:
                        date_date = "create_date = '%s'" % (production.actual_complete_date)
                        where_id = "id = %s" % (svl.id)
                        sql = """ update stock_valuation_layer set %s where %s """ % (date_date, where_id)
                        self.env.cr.execute(sql)

    def write(self, vals):
        for move_line in self:
            production = move_line.move_id.production_id or move_line.move_id.raw_material_production_id
            if production and production.actual_complete_date:
                vals['date'] = production.actual_complete_date
        return super(StockMoveLine, self).write(vals)


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    @api.model
    def create(self, values):
        res = super(StockValuationLayer, self).create(values)
        production = res.stock_move_id.production_id or res.stock_move_id.raw_material_production_id
        if res.stock_move_id and production and production.actual_complete_date:
            date_date = "create_date = '%s'" % (production.actual_complete_date)
            where_id = "id = %s" % (res.id)
            sql = """ update stock_valuation_layer set %s where %s """ % (date_date, where_id)
            self.env.cr.execute(sql)
        return res

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.onchange('tipe')
    def _onchange_tipe(self):
        res = {}
        for rec in self:
            if rec.tipe == 'sampling':
                sampling_int = self.env.ref('bmo_inventory.master_type_1').id
                sampling_ext = self.env.ref('bmo_inventory.master_type_2').id
                return {'domain':{'master_type_id':[('id','in',[sampling_int,sampling_ext])]}}