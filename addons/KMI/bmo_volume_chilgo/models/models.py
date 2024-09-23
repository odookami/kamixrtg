# -*- coding: utf-8 -*-

from odoo import models, fields, api


class VolumeChilgo(models.Model):
    _name = 'volume.chilgo'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Volume Chilgo'

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
    
    volume_chilgo_line_one_ids = fields.One2many(
        'volume.chilgo.line.one', 'volume_chilgo_line_one_id', string='Volume Chilgo Line One', tracking=True
    )
    volume_chilgo_line_two_ids = fields.One2many(
        'volume.chilgo.line.two', 'volume_chilgo_line_two_id', string='Volume Chilgo Line Two', tracking=True
    )
    volume_chilgo_line_three_ids = fields.One2many(
        'volume.chilgo.line.three', 'volume_chilgo_line_three_id', string='Volume Chilgo Line Three', tracking=True
    )

class VolumeChilgoLineOne(models.Model):
    _name = 'volume.chilgo.line.one'
    _description = 'Volume Chilgo Line One'

    name = fields.Integer(
        'Number of Nozzle')
    std_volume = fields.Char(
        'Std Volume Weight (g)')
    volume = fields.Char(
        '130 ± 5 mL Volume (mL)')
    
    
    volume_chilgo_line_one_id = fields.Many2one(
        'volume.chilgo','Volume Chilgo Line One')

class VolumeChilgoLineTwo(models.Model):
    _name = 'volume.chilgo.line.two'
    _description = 'Volume Chilgo Line Two'

    name = fields.Integer(
        'Number of Nozzle')
    std_volume = fields.Char(
        'Std Volume Weight (g)')
    volume = fields.Char(
        '130 ± 5 mL Volume (mL)')
    

    volume_chilgo_line_two_id = fields.Many2one(
        'volume.chilgo','Volume Chilgo Line Two')

class VolumeChilgoLineThree(models.Model):
    _name = 'volume.chilgo.line.three'
    _description = 'Volume Chilgo Line Three'

    name = fields.Integer(
        'Number of Nozzle')
    std_volume = fields.Char(
        'Std Volume Weight (g)')
    volume = fields.Char(
        '130 ± 5 mL Volume (mL)')

    volume_chilgo_line_three_id = fields.Many2one(
        'volume.chilgo','Volume Chilgo Line Three')