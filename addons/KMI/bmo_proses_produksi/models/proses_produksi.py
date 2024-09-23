from asyncore import write
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProsesProduksi(models.Model):
    _name = 'bmo.proses.produksi'
    _description = 'Proses Produksi'

    name = fields.Char(string='Number')
    proses_produksi_line = fields.One2many('bmo.proses.line', 
        inverse_name='proses_id', string='Detail MPP')
    produk_id = fields.Many2one(comodel_name='product.product', string='Produk')
    tanggal = fields.Date(string='Tanggal', tracking=True, default=datetime.today())
    versi = fields.Integer(string='Versi')
    state = fields.Selection(string='Status', selection=[('draft', 'Draft'), 
        ('in_progress', 'In Progress'), ('done', 'Done'),
        ('export', 'Export')], default='draft')

    def action_submit(self):
        return self.write({'state': 'in_progress'})

    def action_done(self):
        return self.write({'state': 'done'})
    
    def action_export(self):
        return self.write({'state': 'done'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('bmo.proses.produksi')
        if 'proses_produksi_line' not in vals:
            raise ValidationError(("Detail Informasi Tahapan Proses Produksi Wajib Diisi !"))
        return super(ProsesProduksi, self).create(vals)

class RealisasiLine(models.Model):
    _name = 'bmo.proses.line'
    
    proses_id = fields.Many2one('bmo.proses.produksi', string='Proses Produksi')
    flow_proses = fields.Image(string="Flow Proses")
    penjelasan = fields.Text(string='Penjelasan dan Acuan')
    catatan = fields.Text(string='Catatan')
    gambar_penjelasan = fields.Image(string="Gambar Penjelasan dan Acuan")



    
    
    