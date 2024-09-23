# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class kmiBatchReport(models.Model):
# 	_name = 'kmi.batch.report'
# 	_description = 'Line Batch Report'

# 	batch_number = fields.Char('No BO / Batch')
# 	no_batch = fields.Selection([('1', 'A1'), ('2', 'A2'),
# 		('3', 'A3'),('4', 'A4')], 'No BO / Batch') # Field ini tidak dipakai, dan tidak bisa direplace tipe field-nya
# 	product_id = fields.Many2one('product.product', string='Product Name')
# 	start_coding = fields.Float('Start Coding Btl')
# 	end_coding = fields.Float('Finish Coding Btl')
# 	output_batch = fields.Selection([('1', '5000'), ('2', '49000'),
# 		('3', '51000'),('4', '49900')], string='output/batch (btl)')
# 	reject_batch = fields.Selection([('1', '25'), ('2', '50'),
# 		('3', '11'),('4', '4')], string='Reject/batch (btl)')

# class KmiChecksParameters(models.Model):
# 	_name = 'kmi.checks.params'
# 	_description = 'Master Data Parameter'

# 	# * GENERAL CHECKS PARAMETERS
# 	active = fields.Boolean(string='Active', default=True)
# 	name = fields.Char(string='Parameter', copy=False)
# 	standard = fields.Char(string='Std')
# 	actual = fields.Char(string='Actual')
# 	param_group = fields.Char(string='Group Parameter')
# 	report_type = fields.Selection([('Packing', 'Packing'), 
# 		('Labeling', 'Labeling'), ('UnLoader', 'UnLoader'), 
# 		('Retort', 'Retort'), ('Loader', 'Loader'),
# 		('Unscramble Machine', 'Unscramble Machine'), 
# 		('Filling Machine', 'Filling Machine'),], 
# 		'Tipe Laporan Harian', copy=False)
# 	param_types = fields.Selection([('machine', 'Machine'), 
# 		('production', 'Production'), ('record', 'Production Record'), 
# 		('general', 'General Checks')], 'Tipe Parameter', copy=False)