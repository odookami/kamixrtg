# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class bmo_unscramble(models.Model):
    _name = 'bmo.unscramble'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Unscramble'

    name = fields.Char('Name')
    date = fields.Date(
        'Tanggal', default=fields.Date.today()
    )
    hal = fields.Char(
        'Hal', tracking=True
    )
    revisi = fields.Char(
        'Revisi', default='0', tracking=True
    )
    report_type = fields.Selection([('Packing', 'Packing'), ('Labeling', 'Labeling'), 
        ('UnLoader', 'UnLoader'), ('Retort', 'Retort'), ('Loader', 'Loader'),
        ('Unscramble Machine', 'Unscramble Machine'), 
        ('Filling Machine', 'Filling Machine'),], 'Tipe Laporan', copy=False)
    operator_id = fields.Many2one('res.users', string='Operator', copy=False)
    leader_id = fields.Many2one('res.users', string='Leader/Supervisor', copy=False)

    # general report
    preparation = fields.Float('Preparation')
    total_breakdown = fields.Float('Total Breakdown')
    running_hours = fields.Float('Running Hours')
    total_reject_unscramble_a = fields.Float('Total Reject Unscramble A')
    total_reject_unscramble_b = fields.Float('Total Reject Unscramble B')
    total_reject_rinser = fields.Float('Total Reject Rinser')
    speed_max_unscramble_a = fields.Float('Speed Max Unscramble A')
    speed_max_unscramble_b = fields.Float('Speed Max Unscramble B')

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
        ('80', '80'),('100', '100'),('140', '140')], string='Kemasan (ml)', tracking=True
    )
    line_machine = fields.Selection([
        ('a', 'A'),('b', 'B'),('c', 'C')], string='Line Machine', tracking=True
    )
    product_name_batch = fields.Char('Product Name/Batch')
    start_production_time = fields.Char('Start Production Time')
    counter_rinser = fields.Char('Counter Rinser')

    # production notes
    prod_note = fields.Char('Production Notes')

    # general check
    checks_line = fields.One2many('kmi.general.checks', 
        'daily_report_id', string='General Checks')
    params_mch_line = fields.One2many('kmi.params.value', 
        'report_mch_id', string='Parameter Machine')
    detail_mch_line = fields.One2many('kmi.params.detail.value', 
        'param_mch_id', string='Detail Value Parameter Machine')
    
    bottle_record_silo_a_ids = fields.One2many(
        'bmo.unscramble.line', 'bottle_record_silo_a_id', string='Bottle Record Silo A', tracking=True
    )
    bottle_record_silo_b_ids = fields.One2many(
        'bmo.unscramble.line', 'bottle_record_silo_b_id', string='Bottle Record Silo B', tracking=True
    )


    # air_pressure_unscramble_a = fields.Char('Air Presure unscramble A (bar)')
    # air_pressure_unscramble_b = fields.Char('Air Presure unscramble B (bar)')
    # air_pressure_rinser_input = fields.Char('Air pressure Rinser Input (Mpa)©')
    # air_pressure_rinser_output = fields.Char('Air pressure rinser Output (psi)©')
    # manual_oil_rinser_level = fields.Char('Manual Oil rinser level')
    # automatic_oil_rinser_level = fields.Char('Automatic Oil rinser level')
    # automatic_oil_unscramble_a_level = fields.Char('Automatic oil unscramble A level')
    # automatic_oil_unscramble_b_level = fields.Char('Automatic oil unscramble B level')
    # machine_hour_rinser = fields.Char('Machine Hour rinser')
    # machine_hour_unsc_a = fields.Char('Machine hours unsc. A')
    # machine_hour_unsc_b = fields.Char('Machine hours unsc. B')
    # baut_rinser_gripper = fields.Char('Baut Rinser Gripper')
    # tekanan_angin = fields.Char('Tekanan Angin dari mangkok supply')
    # blower_air_condition = fields.Char('Blower air condition')
    # air_conveyor_condition = fields.Char('Air Conveyor condition')
    # perputaran_gate = fields.Char('Perputaran gate bottle,sabit,starwheel dan holder bottle unsc')
    # storage_motor_unsc = fields.Char('Storate Motor unsc.')
    # laju_bottle = fields.Char('Laju bottle di jalur air conveyor')
    # note = fields.Char('Notes')

    # parameter mesin
    time_check = fields.Char('Time Check')
    air_pressure_rinser_input = fields.Char('Air pressure Rinser Input ( > 4 Mpa)©')
    air_pressure_rinser_output = fields.Char('Air pressure rinser output ( > 60 psi)©')
    speed_rinser = fields.Char('Speed Rinser')
    speed_unscramble_a = fields.Char('Speed Unscramble A')
    speed_unscramble_b = fields.Char('Speed Unscramble B')
    counter_rinser = fields.Char('Counter Rinser')
    note = fields.Char('Notes')

class bmo_unscramble_line(models.Model):
    _name = 'bmo.unscramble.line'
    _description = 'Unscramble Line'

    # BOTTLE RECORD SILO A & B
    bottle_id = fields.Many2one('product.product', string='Bottle code/name')
    lot = fields.Char('LOT')
    supplier = fields.Many2one('res.partner', string='Supplier')
    time = fields.Datetime('Time')
    bottle_in  = fields.Char('In')
    bottle_out  = fields.Char('Out')
    stock_akhir = fields.Char('Stock Akhir')

    bottle_record_silo_a_id = fields.Many2one(
        'bmo.unscramble', string='Bottle Record Silo A'
    )
    bottle_record_silo_b_id = fields.Many2one(
        'bmo.unscramble', string='Bottle Record Silo B'
    )