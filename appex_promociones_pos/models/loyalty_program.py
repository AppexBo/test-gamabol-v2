# models/loyalty_program.py
from odoo import models
import logging

_logger = logging.getLogger(__name__)

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    def _export_for_pos_ui(self):
        res = super()._export_for_pos_ui()
        for reward in res.get('rewards', []):
            reward_obj = self.env['loyalty.reward'].browse(reward['id'])
            reward['apply_multiple'] = reward_obj.apply_multiple
        return res
