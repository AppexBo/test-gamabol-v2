from odoo import models, fields

class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    is_multi_2x1 = fields.Boolean(string='¿Aplicar 2x1 múltiple?')