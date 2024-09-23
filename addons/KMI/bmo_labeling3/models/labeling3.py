
from ctypes import string_at
from odoo import models, fields, api
from datetime import date

class bmo_labeling3(models.Model):
    _name = 'bmo.labeling3'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Labeling Obol L3'

    name = fields.Char(
        'Name', default='FRM-PRD-', tracking=True
    )
    date = fields.Date(
        'Tanggal', default=fields.Date.today(), tracking=True
    )
    num_of_pages = fields.Char(
        'Hal', tracking=True
    )
    revision = fields.Char(
        'Revisi', default='0', tracking=True
    )
    report_type = fields.Selection([('Packing', 'Packing'), ('Labeling', 'Labeling'), 
        ('UnLoader', 'UnLoader'), ('Retort', 'Retort'), ('Loader', 'Loader'),
        ('Unscramble Machine', 'Unscramble Machine'), 
        ('Filling Machine', 'Filling Machine'),], 'Tipe Laporan', copy=False)
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), 
        ('done', 'Done'), ('cancel', 'Cancel')], 'Status', default='draft', copy=False)
    another_note = fields.Text(string='Another Awesome Notes', copy=False,
        default=""" * Condition OK means : clean, no straching sound, in a good shape
            * Machine stop under 30 min ditulis pada minor breakdown (Form Efficiency)
            * SPV melakukan tanda tangan bila mereview form """)
    operator_id = fields.Many2one('res.users', string='Operator', copy=False)
    leader_id = fields.Many2one('res.users', string='Shift Leader/Supervisor', copy=False)

    labeling3_line_ids = fields.One2many(
        'bmo.labeling3.line', 'labeling3_line_id', string='Labeling Obol L3 Line'
    )
    labeling3_konversi_ids = fields.One2many(
        'bmo.labeling3.konversi', 'labeling3_konversi_id', string='Labeling Obol L3 Line'
    )

    # Prod Notes
    tanggal = fields.Date(
        'Tanggal', tracking=True
    )
    another_note = fields.Text(string='Another Awesome Notes', copy=False,
        default=""" 
            * Condition OK means : clean, no straching sound, in a good shape
            * Machine stop under 30 min ditulis pada minor breakdown (Form Efficiency)
            * SPV melakukan tanda tangan bila mereview form
            * Bila belt leak check kotor, segera dibersihkan dengan brush dan air per 2 jam
            * Reject SLA yang dibuang pada saat produksi """)
    dayofweek = fields.Selection([('0', 'Senin'), ('1', 'Selasa'),
        ('2', 'Rabu'), ('3', 'Kamis'), ('4', 'Jumat'),
        ('5', 'Sabtu'), ('6', 'Minggu')], 'Hari')
    shift = fields.Selection([('I', 'I'), ('II', 'II'),
        ('III', 'III')], string='Shift')
    note = fields.Text('Notes: ')


    # CATATAN KETIDAKSESUAIAN SELAMA PROSES PRODUKSI
    # catatan breakdown
    incompatibility_line = fields.One2many('kmi.incompatibility.notes', 
        'daily_report_id', string='Catatan Proses Produksi')
    # start = fields.Datetime('Start')
    # stop = fields.Datetime('Stop')
    # total = fields.Integer('total')
    # uraian = fields.Char('Uraian Masalah')
    # frekuensi = fields.Char('Frekuensi')
    # status = fields.Char('Status')
    # pic = fields.Char('PIC')

    
class bmo_labeling3_line(models.Model):
    _name = 'bmo.labeling3.line'
    _description = 'Labeling Obol L3 Line'

    change_time = fields.Date('Change Time')
    code_id = fields.Many2one(
        'product.product', string='Item Code'
    )
    lot_id = fields.Char('Lot No')
    roll = fields.Integer('Roll')
    kilo = fields.Integer(string='KG')
    start = fields.Datetime('Start')
    finish = fields.Datetime('Finish')
    in_minute = fields.Float('In Minute')
    code_batch = fields.Integer('Code Batch')
    out_minute = fields.Float('Out Minute')
    reject = fields.Float('Reject')
    last_stock = fields.Float('Last Stock')
    re_turn = fields.Float('Return')
    join = fields.Integer('Join')
    actual = fields.Integer('Actual')
    splice = fields.Integer('KMI splice')
    konversi = fields.Float('Konversi usage kg ke roll')
    labeling3_line_id = fields.Many2one(
        'bmo.labeling3', string='Labeling Obol L3 Line'
    )

class bmo_labeling3_konversi(models.Model):
    _name = 'bmo.labeling3.konversi'
    _description = 'Labeling Obol L3 Koversi'

    product_cgm_id = fields.Many2one('product.product', string='Produk CGM/HI C')
    product_nbe_id = fields.Many2one('product.product', string='Produk NBE/Fishot')
    hi_c = fields.Char('hi c')
    jumlah = fields.Integer('Jumlah')
    meter = fields.Float('M')
    standart = fields.Float('Standar (m)')
    reject = fields.Float('Reject')
    total_reject = fields.Float('Total Reject')
    labeling3_konversi_id = fields.Many2one(
        'bmo.labeling3', string='Labeling Obol L3 Line'
    )