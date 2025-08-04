from odoo import models

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    def _export_for_pos_ui(self):
        res = super()._export_for_pos_ui()
        for reward in res['rewards']:
            reward_id = reward.get('id')
            reward_obj = self.env['loyalty.reward'].browse(reward_id)
            reward['apply_multiple'] = reward_obj.apply_multiple
        return res
