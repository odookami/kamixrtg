# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Loader(models.Model):
    _name = 'loader'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Loader'

    name = fields.Char(
        'Name', tracking=True
    )
    date = fields.Date(
        'Hari / Tanggal', default=fields.Date.today(), tracking=True
    )
    shift = fields.Selection([
        ('1', 'I'),('2', 'II'),('3', 'III')], string='Shift', tracking=True
    )
    team = fields.Selection([
        ('a', 'A'),('b', 'B'),('c', 'C'),('d', 'D')], string='Team', tracking=True
    )
    line_machine = fields.Selection([
        ('a', 'A'),('b', 'B'),('c', 'C')], string='Line Machine', tracking=True
    )
    hal = fields.Char(
        'Hal', tracking=True
    )
    revisi = fields.Char(
        'Revisi', default='0', tracking=True
    )
    note = fields.Text(
        string='Note')
    preparation = fields.Char(
        'Preparation', tracking=True
    )
    total_breakdown = fields.Char(
        'Total breakdown', tracking=True
    )
    running_hours = fields.Char(
        'Running hours', tracking=True
    )
    total_reject = fields.Char(
        'Total Reject (btl)', tracking=True
    )
    day = fields.Char(
        'Hari', tracking=True
    )
    kemasan = fields.Selection([
        ('80', '20'),('100', '100'),('140', '140')], string='Kemasan', tracking=True
    )
    note_1 = fields.Text(
        'Notes')
    note_2 = fields.Text(
        'Notes')
    keterangan = fields.Text(
        'Pencatatan start/finish jam per keranjang mengacu jam coding pada produk', copy=False,
        default="""
Jam start =  botol terdepan pada layer paling bawah
Jam finish = botol terakhir pada layer paling atas """)



    general_checks_line_ids = fields.One2many(
        'general.checks.line', 'general_checks_line_id', string='General Checks Lines', tracking=True
    )
    production_record_line_ids = fields.One2many(
        'production.record.line', 'production_record_line_id', string='Production Record Lines', tracking=True
    )
    breakdown_line_ids = fields.One2many(
        'breakdown.line', 'breakdown_line_id', string='Breakdown Lines', tracking=True
    )


class GeneralChecksLine(models.Model):
    _name = 'general.checks.line'
    _description = 'General Checks Line'

    parameter = fields.Char(
        'Parameter')
    std = fields.Char(
        'Std')
    actual = fields.Char(
        'Actual')
    

    
    general_checks_line_id = fields.Many2one(
        'loader', string='General Checks Lines', index=True, required=False, ondelete='cascade'
    )

class ProductionRecordLine(models.Model):
    _name = 'production.record.line'
    _description = 'Production Record Line'

    retort_code = fields.Char(
        'Retort code')
    product_name = fields.Many2one(
        'product.product','Product Name')
    cage_1_start = fields.Char(
        'Cage 1 Start')
    cage_1_finish = fields.Char(
        'Cage 1 Finish')
    cage_2_start = fields.Char(
        'Cage 2 Start')
    cage_2_finish = fields.Char(
        'Cage 2 Finish')
    cage_3_start = fields.Char(
        'Cage 3 Start')
    cage_3_finish = fields.Char(
        'Cage 3 Finish')
    cage_4_start = fields.Char(
        'Cage 4 Start')
    cage_4_finish = fields.Char(
        'Cage 4 Finish')

    
    production_record_line_id = fields.Many2one(
        'loader', string='Production Record Lines', index=True, required=False, ondelete='cascade'
    )

class BreakdownLine(models.Model):
    _name = 'breakdown.line'
    _description = 'Breakdown Line'

    no = fields.Char(
        'No.')
    start = fields.Char(
        'Start')
    finish = fields.Char(
        'Finish')
    total = fields.Char(
        'Total')
    uraian_masalah = fields.Char(
        'Uraian Masalah')
    frekuensi = fields.Char(
        'Frekuensi')
    status = fields.Char(
        'Status')
    pic = fields.Char(
        'PIC')

    
    breakdown_line_id = fields.Many2one(
        'loader', string='Breakdown Lines', index=True, required=False, ondelete='cascade'
    )