from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round

from itertools import groupby
from odoo.addons.bmo_mrp.models.product import state_tipe

class DataRevisi(models.Model):
    _name = 'data.revisi'
    _description = 'Data Revisi'
    
    name = fields.Char('No')
    description = fields.Char('Description')
    
    def name_get(self):
        result = []
        for record in self:
            name = "%s.  %s" % (record.name,record.description)
            result.append((record.id, name))
        return result
    
class RevisiBoM(models.Model):
    _name = "revisi.bom"
    _description = 'Revisi BoM'
    _order = 'name desc'
    
    name = fields.Char('Version')
    bom_id = fields.Many2one('mrp.bom', 'BoM', ondelete='cascade')
    date = fields.Datetime("Date")
    user_id = fields.Many2one('res.users', 'User')
    data_revisi_id = fields.Many2one('data.revisi', 'Type')
    description = fields.Text('Description')
    
    
class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    tipe = fields.Selection(state_tipe, string='Type')
    version = fields.Integer('Version', default=0)
    state = fields.Selection(
        [('draft','Draft'),('confirmed','Confirmed'),('done','Run')], string='Status', default='draft')
    revisi_ids = fields.One2many('revisi.bom', 'bom_id', string='Revision')
    code_bon = fields.Char("Code Bom")
    
    def action_confirmed(self):
        user_manager_id = self.env['res.company']._company_default_get('res.config.settings').user_manager_id
        for rec in self:
            notification_ids = []
            notification_ids.append((0,0,{
            'res_partner_id':user_manager_id.partner_id.id,
            'notification_type':'inbox'}))
            body = f'Mohon Untuk Di Confirmed BoM No. {self.code}'
            self.message_post(body=body, message_type='notification', notification_ids=notification_ids)
            rec.write({'state' : 'confirmed'})
    
    def action_done(self):
        for rec in self:
            rec.write({'state' : 'done'})
    
    