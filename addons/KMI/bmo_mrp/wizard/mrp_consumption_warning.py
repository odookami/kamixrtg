from odoo import fields, models, api


class MrpConsumptionWarning(models.TransientModel):
    _inherit = 'mrp.consumption.warning'


    def action_confirm(self):
        action_from_do_finish = False
        if self.env.context.get('from_workorder'):
            if self.env.context.get('active_model') == 'mrp.workorder':
                action_from_do_finish = self.env['mrp.workorder'].browse(self.env.context.get('active_id')).do_finish()
        action_from_mark_done = self.mrp_production_ids.with_context(skip_consumption=True).button_mark_done()
        return action_from_do_finish or action_from_mark_done