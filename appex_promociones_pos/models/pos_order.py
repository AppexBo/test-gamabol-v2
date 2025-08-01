from odoo import models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _apply_2x1_promotion(self):
        rules = self.env['pos.loyalty.rule'].search([('is_multi_2x1', '=', True)])

        for rule in rules:
            promo_products = rule.product_ids.ids
            for order in self:
                lines = [line for line in order.lines if line.product_id.id in promo_products]
                lines.sort(key=lambda l: l.price_unit)

                pairs = len(lines) // rule.min_quantity if rule.min_quantity else len(lines) // 2
                for i in range(pairs):
                    index = i * rule.min_quantity + rule.min_quantity - 1
                    if index < len(lines):
                        lines[index].write({'discount': 100})

    def create_from_ui(self, orders, draft=False):
        res = super().create_from_ui(orders, draft)
        for order in self.browse([o['id'] for o in res if o.get('id')]):
            order._apply_2x1_promotion()
        return res