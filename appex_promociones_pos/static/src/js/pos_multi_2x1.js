/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { LoyaltyLoader } from "@point_of_sale/app/models/loyalty_program/loyalty_program_loader";
import { Order } from "@point_of_sale/app/store/models/order";

// 🧩 Patch al loader: para incluir apply_multiple
patch(LoyaltyLoader.prototype, {
    async _processData(loadedData) {
        this.couponCache = {};
        this.partnerId2CouponIds = {};
        this.rewards = loadedData["loyalty.reward"] || [];

        for (const reward of this.rewards) {
            reward.all_discount_product_ids = new Set(reward.all_discount_product_ids);
        }

        this.fieldTypes = loadedData["field_types"];
        await super._processData(loadedData);

        this.productId2ProgramIds = loadedData["product_id_to_program_ids"];
        this.programs = loadedData["loyalty.program"] || [];
        this.rules = loadedData["loyalty.rule"] || [];

        // ✅ Marcar apply_multiple como booleano para usarlo en frontend
        for (const reward of this.rewards) {
            reward.apply_multiple = !!reward.apply_multiple;
        }

        this._loadLoyaltyData();
    },
});

// 🧩 Patch al modelo Order: para aplicar recompensa varias veces
patch(Order.prototype, {
    getPotentialFreeProductRewards(couponProgram) {
        const result = [];
        const program = this.pos.program_by_id[couponProgram.program_id];
        const points = this.getLoyaltyPoints(program);

        for (const reward of program.rewards.filter(r => r.reward_type === 'product' && r.reward_product_ids.length > 0)) {
            const allowMultiple = reward.apply_multiple ?? false;

            const applicableQty = this
                .get_orderlines()
                .filter(l => !l.is_reward_line && reward.reward_product_ids.includes(l.product.id))
                .reduce((sum, line) => sum + line.quantity, 0);

            const setsOfTwo = Math.floor(applicableQty / 2);
            const rewardQty = allowMultiple ? setsOfTwo : setsOfTwo > 0 ? 1 : 0;

            const requiredPointsTotal = reward.required_points * rewardQty;

            if (rewardQty >= 1 && points >= requiredPointsTotal) {
                result.push({
                    coupon_id: couponProgram.coupon_id,
                    reward,
                    potentialQty: rewardQty,
                });
            }
        }

        return result;
    },
});
