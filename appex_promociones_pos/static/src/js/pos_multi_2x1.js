/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models/order";

// Interceptar descuentos por lealtad
patch(Order.prototype, {
    async getPotentialDiscountRewards(couponProgram) {
        const program = this.pos.program_by_id[couponProgram.program_id];
        const points = this.getLoyaltyPoints(program);

        const result = [];

        for (const reward of program.rewards.filter(r => r.reward_type === 'discount')) {
            const applicableLines = this.get_orderlines().filter(
                (line) =>
                    !line.is_reward_line &&
                    (!reward.all_discount_product_ids.size || reward.all_discount_product_ids.has(line.product.id))
            );

            const subtotal = applicableLines.reduce((sum, line) => sum + line.get_base_price(), 0);
            const discountAmount = reward.discount_type === 'percentage'
                ? (subtotal * reward.discount) / 100
                : reward.discount;

            if (discountAmount > 0 && points >= reward.required_points) {
                console.log("Hola mundo, se aplicó el descuento");
                result.push({
                    coupon_id: couponProgram.coupon_id,
                    reward,
                    potentialDiscount: discountAmount,
                });
            }
        }

        return result;
    },
});
