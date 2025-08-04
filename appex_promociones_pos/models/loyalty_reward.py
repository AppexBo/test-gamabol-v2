from odoo import models, fields

class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    apply_multiple = fields.Boolean("Aplicar múltiples veces", default=False)
