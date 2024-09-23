from datetime import datetime
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
import time
import calendar
from odoo import _, api, fields, models, SUPERUSER_ID, tools

class wizard_revisi(models.TransientModel):
    _name = "wizard.revisi"
    _description = "Revisi Reason wizard"

    data_revisi_id = fields.Many2one('data.revisi', 'Type', required=True)
    employee_id = fields.Many2one(
        'hr.employee', string='Employee', readonly=True, default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1))
    description_reason = fields.Text(string='Reason', required=True)

    def revisi_bom(self):
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        bom = self.env['mrp.bom'].browse(active_ids)
        version = int(bom.version)
        version_plus = version + 1
        self.env['revisi.bom'].create({
            'bom_id'        : bom.id,
            'name'          : version,
            'date'          : datetime.now(),
            'user_id'       : self.env.user.id,
            'data_revisi_id': self.data_revisi_id.id,
            'description'   : self.description_reason,
        })
        bom.update({
            'version'   : version_plus,
            'state'     : 'draft'
        })
        