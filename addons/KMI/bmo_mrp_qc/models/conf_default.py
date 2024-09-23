from odoo import models, fields, api, _

class MasterSequence(models.Model):
    _name = 'master.sequence'
    _description = 'Master Sequence'
    _rec_name = "number"

    number = fields.Integer("NUmber")

class Master_QC(models.Model):
    _name = 'master.qc'
    _description = 'Master QC'
    _rec_name = "tipe_category"

    name = fields.Char("Document")
    tipe_category = fields.Many2one(
        "type.category", "Type Category")
    version = fields.Char("Version")
    date = fields.Date("Date")
    master_qc_lines = fields.One2many(
        'master.qc.line', 'master_id', 'Master QC Lines', copy=True)
    #Archieve
    active = fields.Boolean('Active', default=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('done','Done'),
        ], string='Status', default='draft', tracking=True, copy=False,
    )

    def action_submit(self):
        for rec in self:
            rec.state = "submit"
            
    def action_done(self):
        for rec in self:
            rec.state = "done"
    
    def action_draft(self):
        for rec in self:
            rec.state = "draft"

class Master_QC_line(models.Model):
    _name = 'master.qc.line'
    _description = 'Master QC Line'
    _rec_name = "master_id"

    master_id = fields.Many2one(
        'master.qc', 'Master QC', required=True, ondelete='cascade')
    sequence_ids = fields.Many2many(
        "master.sequence", string="Titik sampling")
    tipe_category = fields.Many2one(
        "type.category", "Type Category", related="master_id.tipe_category", store=True)
    master_data_qc_lines = fields.One2many(
        'master.data.qc.line', 'master_data_id', 'Master Data QC Lines', copy=True)
    #Archieve
    active = fields.Boolean(
        'Active', related="master_id.active", store=True)

class Master_Data_QC_line(models.Model):
    _name = 'master.data.qc.line'
    _description = 'Master Data QC Line'

    master_data_id = fields.Many2one(
        'master.qc.line', 'Master Data QC', required=True, ondelete='cascade')
    test_calss = fields.Selection(
        [("PHYSICAL","PHYSICAL"),("MICRO","MICRO"),("CHEMICAL","CHEMICAL")], string="Test Class")
    name = fields.Char("Test Parameter")
    unit = fields.Char(
        "Test Unit")
    value_char = fields.Char(
        "Value Char")
    min_value_num = fields.Char(
        "Min Value Num")
    max_value_num = fields.Char(
        "Max Value Num")
    #Archieve
    active = fields.Boolean(
        'Active', related="master_data_id.active", store=True)