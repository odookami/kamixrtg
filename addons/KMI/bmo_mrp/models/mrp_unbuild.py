from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools import float_compare


class MrpUnbuild(models.Model):
    _inherit = "mrp.unbuild"

    def action_unbuild(self):
        res = super(MrpUnbuild, self).action_unbuild()
        if self.mo_id:
            self.mo_id.write({'unbuild' : True, 'state' : 'cancel'})
        return res
    
    def action_update_mo(self):
        for rec in self:
            if rec.mo_id:
                rec.mo_id.write({'unbuild' : True, 'state' : 'cancel'})
                rec.mo_id.bache_id._compute_qty_production()