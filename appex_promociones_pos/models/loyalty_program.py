from odoo import models
import logging

_logger = logging.getLogger(__name__)

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    def _export_for_pos_ui(self):
        _logger.warning("***** ENTRANDO A EXPORTACIÓN DE POS *****")
        res = super()._export_for_pos_ui()

        for reward in res.get('rewards', []):
            reward_obj = self.env['loyalty.reward'].browse(reward['id'])
            _logger.warning(f"Recompensa {reward_obj.id} - apply_multiple: {reward_obj.apply_multiple}")
            reward['apply_multiple'] = reward_obj.apply_multiple

        return res
