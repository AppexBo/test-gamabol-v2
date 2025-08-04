import logging
_logger = logging.getLogger(__name__)

class LoyaltyProgram(models.Model):
    _inherit = 'loyalty.program'

    def _export_for_pos_ui(self):
        res = super()._export_for_pos_ui()
        _logger.info("Exportando recompensas para POS")
        for reward in res.get('rewards', []):
            reward_obj = self.env['loyalty.reward'].browse(reward['id'])
            _logger.info(f"Recompensa {reward_obj.id} apply_multiple: {reward_obj.apply_multiple}")
            reward['apply_multiple'] = reward_obj.apply_multiple
        return res
