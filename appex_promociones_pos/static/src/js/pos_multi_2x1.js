/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { LoyaltyProgram } from "@point_of_sale/app/models/loyalty_program/loyalty_program";

patch(LoyaltyProgram.prototype, {
    getApplicableRewards(order) {
        const rewards = [];
        for (const rule of this.rules) {
            const reward = this.getRewardByRule(rule);
            if (reward) {
                const lines = order.get_orderlines().filter(line =>
                    rule.product_ids.includes(line.product.id)
                );

                let totalQty = lines.reduce((sum, line) => sum + line.quantity, 0);

                if (rule.apply_multiple) {
                    const times = Math.floor(totalQty / rule.min_quantity);
                    if (times >= 1) {
                        for (let i = 0; i < times; i++) {
                            rewards.push(reward);
                        }
                    }
                } else {
                    // default Odoo behavior
                    if (totalQty >= rule.min_quantity) {
                        rewards.push(reward);
                    }
                }
            }
        }
        return rewards;
    },
});
