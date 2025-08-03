/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    getClaimableRewards(onlyManual, withCoupon, skipAppliedRewards) {
        const rewards = [];
        const order = this;
        const orderlines = order.orderlines;

        for (const program of order.pos.programs) {
            for (const reward of program.rewards) {
                if (reward.reward_type !== "discount") {
                    continue;
                }

                // Obtener productos válidos definidos en la regla
                const validProductIds = new Set(
                    reward.program_id.rules.flatMap(rule => rule.valid_product_ids || [])
                );

                if (!validProductIds.size) {
                    continue; // No hay productos válidos definidos
                }

                // Contar cuántas unidades de productos válidos hay en el carrito
                const matchingQty = orderlines
                    .filter(line => validProductIds.has(line.product.id))
                    .reduce((sum, line) => sum + line.quantity, 0);

                // Verificamos si se cumple la cantidad mínima
                const minQty = reward.program_id.rules[0].min_quantity || 1;
                const applicableTimes = Math.floor(matchingQty / minQty);

                if (applicableTimes > 0) {
                    for (let i = 0; i < applicableTimes; i++) {
                        rewards.push({
                            reward: reward,
                            coupon_id: null,
                        });
                    }
                }
            }
        }

        return rewards;
    },
});
