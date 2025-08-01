from odoo import models, fields

class LoyaltyRule(models.Model):
    _inherit = 'loyalty.rule'

    apply_multiple = fields.Boolean("Aplicar múltiples veces", default=False)