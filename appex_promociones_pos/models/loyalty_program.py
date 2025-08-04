from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _load_pos_data(self, data):
        data = super()._load_pos_data(data)

        # Registramos un log para asegurarnos de que entramos
        _logger.warning(">>> Cargando datos extendidos para POS")

        for reward in self.env['loyalty.reward'].search([]):
            _logger.warning(f"Recompensa ID {reward.id} - apply_multiple: {reward.apply_multiple}")

        # Recorremos todos los programas de fidelización cargados
        for program in data['data'][0].get('loyalty.program', []):
            # Por cada recompensa del programa, añadimos apply_multiple si existe
            for reward in program.get('rewards', []):
                reward_id = reward.get('id')
                if reward_id:
                    reward_obj = self.env['loyalty.reward'].browse(reward_id)
                    reward['apply_multiple'] = reward_obj.apply_multiple
                    _logger.warning(f"→ Añadiendo apply_multiple a reward {reward_id}: {reward_obj.apply_multiple}")

        return data
