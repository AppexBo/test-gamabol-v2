from odoo import models, fields

class LoyaltyReward(models.Model):
    _inherit = 'loyalty.reward'

    discount_applicability = fields.Selection([
        ('order', 'Order'),
        ('cheapest', 'Cheapest Product'),
        ('specific', 'Specific Products'),
        ('apply_multiple', 'Promoción 2x1 múltiple')
    ], default='order')
