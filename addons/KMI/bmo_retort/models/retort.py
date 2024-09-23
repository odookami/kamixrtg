
from odoo import models, fields, api
from datetime import date

class Retort(models.Model):
    _name = 'retort'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Retort'

    name = fields.Char(
        'Name', default='FRM-PRD-', tracking=True
    )
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'), 
        ('done', 'Done'), ('cancel', 'Cancel')], 'Status', default='draft', copy=False)
    date = fields.Date(
        'Hari / Tanggal', default=fields.Date.today(), tracking=True
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

    # bottom
    another_note = fields.Text(string='Another Awesome Notes', copy=False,
        default=""" * Condition OK means : clean, no straching sound, in a good shape
            * Machine stop under 30 min ditulis pada minor breakdown (Form Efficiency)
            * SPV melakukan tanda tangan bila mereview form
            * Range grafik chil go: 121˚C              , Benecol : 100˚C
            © = CCP """)
    operator_id = fields.Many2one('res.users', string='Operator', copy=False)
    leader_id = fields.Many2one('res.users', string='Shift Leader', copy=False)
    spv_id = fields.Many2one('res.users', string='SPV/Manger', copy=False)

    # general report
    preparation = fields.Float(
        'Preparation', tracking=True
    )
    total_breakdown = fields.Float(
        'Total breakdown', tracking=True
    )
    running_hours = fields.Float(
        'Running hours', tracking=True
    )
    batch = fields.Char('Batch')
    product_name = fields.Many2one('product.product' ,'Product Name')
    start = fields.Datetime('Start')
    finish = fields.Datetime('Finish')
    note = fields.Text(
        string='Notes')

    # production notes
    hari = fields.Selection([('0', 'Senin'), ('1', 'Selasa'),
        ('2', 'Rabu'), ('3', 'Kamis'), ('4', 'Jumat'),
        ('5', 'Sabtu'), ('6', 'Minggu')], 'Hari')
    tanggal = fields.Date('Tanggal')
    shift = fields.Selection([
        ('1', 'I'),('2', 'II'),('3', 'III')], string='Shift', tracking=True
    )
    team = fields.Selection([
        ('a', 'A'),('b', 'B'),('c', 'C'),('d', 'D')], string='Team', tracking=True
    )
    kemasan = fields.Selection([
        ('80', '80'),('100', '100'),('130', '130'),('140', '140'),('180', '180')], string='Kemasan', tracking=True
    )

    # general check
    checks_line = fields.One2many('kmi.general.checks', 
        'daily_report_id', string='General Checks')

    # prod record
    prod_rec_line = fields.One2many('kmi.params.value', 
        'report_prod_rec_id', string='Production Record')

    # catatan breakdown
    incompatibility_line = fields.One2many('kmi.incompatibility.notes', 
        'daily_report_id', string='Catatan Proses Produksi')

    