# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VisualProduk(models.Model):
    _name = 'visual.produk'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Visual Produk'

    name = fields.Char(
        'Name', tracking=True
    )
    date = fields.Date(
        'Hari / Tanggal', default=fields.Date.today(), tracking=True
    )
    shift = fields.Selection([
        ('1', 'I'),('2', 'II'),('3', 'III')], string='Shift', tracking=True
    )
    product_name = fields.Many2one(
        'product.product', 'Nama Produk', tracking=True)
    product_prod = fields.Char(
        string='Prod. Date', default=fields.Date.today(), tracking=True)
    product_batch = fields.Char(
        'Batch')
    product_weight = fields.Char(
        'Weight Tare (g)')
    product_sg = fields.Char(
        'SG (g/mL)')
    speed_filling = fields.Char(
        string='Speed Filling')
    filling_prod = fields.Char(
        string='Prod. Date', default=fields.Date.today(), tracking=True)
    filling_batch = fields.Char(
        'Batch')
    filling_weight = fields.Char(
        'Weight Tare (g)')
    filling_sg = fields.Char(
        'SG (g/mL)')
    type_of_bottle = fields.Char(
        string='Type of Bottle')
    bottle_prod = fields.Char(
        string='Prod. Date', default=fields.Date.today(), tracking=True)
    bottle_batch = fields.Char(
        'Batch')
    bottle_weight = fields.Char(
        'Weight Tare (g)')
    bottle_sg = fields.Char(
        'SG (g/mL)')
    hal = fields.Char(
        'Hal', tracking=True
    )
    revisi = fields.Char(
        'Revisi', default='0', tracking=True
    )
    menggantikan_no = fields.Char(
        'Menggantikan No.')
    tanggal_menggantikan = fields.Char(
        'Tanggal Menggantikan')
    note = fields.Text(
        string='CATATAN')
    check = fields.Char(
        string='Diperiksa oleh :')
    check_date = fields.Date(
        'Tanggal Diperiksa :', default=fields.Date.today(), tracking=True)
    approved = fields.Char(
        'Disetujui oleh :')
    approved_date = fields.Date(
        'Tanggal Disetujui :', default=fields.Date.today(), tracking=True)
    conclusion = fields.Char(
        'Kesimpulan :')
    max_1 = fields.Char(
        'Max')
    min_1 = fields.Char(
        'Min')
    average_1 = fields.Char(
        'Average')
    pic_analisa_1 = fields.Char(
        'PIC Analisa')
    tgl_analisa_1 = fields.Date(
        'Tanggal Analisa', default=fields.Date.today(), tracking=True)
    jam_analisa_1 = fields.Char(
        'Jam Analisa')
    max_2 = fields.Char(
        'Max')
    min_2 = fields.Char(
        'Min')
    average_2 = fields.Char(
        'Average')
    pic_analisa_2 = fields.Char(
        'PIC Analisa')
    tgl_analisa_2 = fields.Date(
        'Tanggal Analisa', default=fields.Date.today(), tracking=True)
    jam_analisa_2 = fields.Char(
        'Jam Analisa')
    max_3 = fields.Char(
        'Max')
    min_3 = fields.Char(
        'Min')
    average_3 = fields.Char(
        'Average')
    pic_analisa_3 = fields.Char(
        'PIC Analisa')
    tgl_analisa_3 = fields.Date(
        'Tanggal Analisa', default=fields.Date.today(), tracking=True)
    jam_analisa_3 = fields.Char(
        'Jam Analisa')
    periksa = fields.Many2one(
        'hr.employee','Diperiksa oleh :')
    tgl_periksa = fields.Date(
        'Tanggal Diperiksa', default=fields.Date.today(), tracking=True)
    setujui = fields.Many2one(
        'hr.employee','Disetujui oleh :')
    tgl_setuju = fields.Date(
        'Tanggal Disetujui :', default=fields.Date.today(), tracking=True)
    kesimpulan = fields.Text(
        'Kesimpulan :')
    catatan = fields.Text(
        'Catatan :')
    ket = fields.Text(
        'Note : ', copy=False,
        default="""    
Standar of Seal Tester / Geprek : Tidak ditemukan adanya potensi kebocoran pada alu cap ataupun hasil sealing (baik dengan alat ataupun manual check)
Standard Visual Condition : Tidak ditemukan adanya botol penyok atau scratch, hasil sealing cap abnormal (overheat, lecet, meleset, terlipat,dll)
""")
    
    visual_produk_line_one_ids = fields.One2many(
        'visual.produk.line.one', 'visual_produk_line_one_id', string='Visual Produk Line One', tracking=True
    )
    visual_produk_line_two_ids = fields.One2many(
        'visual.produk.line.two', 'visual_produk_line_two_id', string='Visual Produk Line Two', tracking=True
    )
    visual_produk_line_three_ids = fields.One2many(
        'visual.produk.line.three', 'visual_produk_line_three_id', string='Visual Produk Line Three', tracking=True
    )

class VisualProdukLineOne(models.Model):
    _name = 'visual.produk.line.one'
    _description = 'Visual Produk Line One'

    name = fields.Integer(
        'Number of Nozzle')
    std_volume = fields.Char(
        'Std Volume Weight (g)')
    volume = fields.Char(
        'Visual Check')
    
    
    visual_produk_line_one_id = fields.Many2one(
       'visual.produk','Visual Produk Line One')

class VisualProdukLineTwo(models.Model):
    _name = 'visual.produk.line.two'
    _description = 'Visual Produk Line Two'

    name = fields.Integer(
        'Number of Nozzle')
    std_volume = fields.Char(
        'Std Volume Weight (g)')
    volume = fields.Char(
        'Visual Check')
    

    visual_produk_line_two_id = fields.Many2one(
        'visual.produk','Visual Produk Line Two')

class VisualProdukLineThree(models.Model):
    _name = 'visual.produk.line.three'
    _description = 'Visual Produk Line Three'

    name = fields.Integer(
        'Number of Nozzle')
    std_volume = fields.Char(
        'Std Volume Weight (g)')
    volume = fields.Char(
        'Visual Check')

    visual_produk_line_three_id = fields.Many2one(
        'visual.produk','Visual Produk Line Three')