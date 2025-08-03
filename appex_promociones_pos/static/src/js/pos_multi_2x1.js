/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

function _getMatchingRuleLines(order, reward) {
    const ruleProducts = reward.program_id.rules.reduce((set, rule) => {
        if (rule.any_product) return new Set();  // Si se aplica a cualquiera
        rule.valid_product_ids.forEach((id) => set.add(id));
        return set;
    }, new Set());

    return order.get_orderlines().filter(line => {
        return (
            !line.reward_id &&
            !line.comboParent &&
            ruleProducts.has(line.product.id)
        );
    });
}

patch(Order.prototype, {

    getClaimableRewards(coupon_id = false, program_id = false, auto = false) {
        const result = [];
        const allCouponPrograms = Object.values(this.couponPointChanges).map(pe => ({
            program_id: pe.program_id,
            coupon_id: pe.coupon_id,
        })).concat(this.codeActivatedCoupons.map(coupon => ({
            program_id: coupon.program_id,
            coupon_id: coupon.id,
        })));

        for (const couponProgram of allCouponPrograms) {
            const program = this.pos.program_by_id[couponProgram.program_id];
            if (!program) continue;

            const points = this._getRealCouponPoints(couponProgram.coupon_id);
            for (const reward of program.rewards) {
                if (reward.reward_type !== "discount") continue;
                if (points < reward.required_points) continue;

                const matchingLines = _getMatchingRuleLines(this, reward);
                const totalQty = matchingLines.reduce((sum, line) => sum + line.quantity, 0);
                const requiredQty = reward.program_id.rules[0]?.min_quantity || 1;
                const applyMultiple = reward.program_id.rules[0]?.apply_multiple;

                let timesApplicable = Math.floor(totalQty / requiredQty);
                if (!applyMultiple && timesApplicable > 1) {
                    timesApplicable = 1;
                }

                if (timesApplicable >= 1) {
                    result.push({
                        coupon_id: couponProgram.coupon_id,
                        reward: reward,
                        potentialQty: timesApplicable,
                    });
                }
            }
        }

        return result;
    },

    _getRewardLineValuesDiscount({ reward, coupon_id, potentialQty }) {
        const matchingLines = _getMatchingRuleLines(this, reward);
        const discountable = matchingLines.reduce((sum, line) => sum + line.get_price_with_tax(), 0);
        if (!discountable) return [];

        const discountLineProduct = reward.discount_line_product_id;
        const maxDiscount = reward.discount * potentialQty;
        const discountAmount = Math.min(discountable, maxDiscount);
        const rewardCode = _newRandomRewardCode();

        return [{
            product: discountLineProduct,
            price: -discountAmount,
            quantity: 1,
            reward_id: reward.id,
            is_reward_line: true,
            coupon_id: coupon_id,
            points_cost: reward.required_points * potentialQty,
            reward_identifier_code: rewardCode,
            merge: false,
            tax_ids: discountLineProduct.taxes_id,
        }];
    },

    _applyReward(reward, coupon_id, args) {
        if (reward.reward_type === "discount") {
            const lines = this._getRewardLineValuesDiscount({ reward, coupon_id, potentialQty: args.potentialQty });
            for (const line of lines) {
                this.add_product(line.product, {
                    quantity: line.quantity,
                    price: line.price,
                    extra: {
                        reward_id: line.reward_id,
                        coupon_id: line.coupon_id,
                        points_cost: line.points_cost,
                        reward_identifier_code: line.reward_identifier_code,
                        is_reward_line: true,
                    },
                    merge: line.merge,
                    tax_ids: line.tax_ids,
                });
            }
        }
    },

    _updateRewardLines() {
        if (!this.orderlines.length) return;

        const rewardLines = this._get_reward_lines();
        if (!rewardLines.length) return;

        for (const line of rewardLines) {
            this.orderlines.remove(line);
        }

        const rewards = this.getClaimableRewards(false, false, false);
        for (const rewardData of rewards) {
            this._applyReward(rewardData.reward, rewardData.coupon_id, {
                potentialQty: rewardData.potentialQty,
            });
        }
    },
});
