/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    getClaimableRewards(coupon_id = false, program_id = false, auto = false) {
        const allCouponPrograms = Object.values(this.couponPointChanges).map((pe) => {
            return {
                program_id: pe.program_id,
                coupon_id: pe.coupon_id,
            };
        }).concat(this.codeActivatedCoupons.map((coupon) => {
            return {
                program_id: coupon.program_id,
                coupon_id: coupon.id,
            };
        }));
        const result = [];
        const totalWithTax = this.get_total_with_tax();
        const totalWithoutTax = this.get_total_without_tax();
        const totalIsZero = totalWithTax === 0;
        const globalDiscountLines = this._getGlobalDiscountLines();
        const globalDiscountPercent = globalDiscountLines.length ? this.pos.reward_by_id[globalDiscountLines[0].reward_id].discount : 0;

        for (const couponProgram of allCouponPrograms) {
            const program = this.pos.program_by_id[couponProgram.program_id];
            if (program.pricelist_ids.length > 0 && (!this.pricelist || !program.pricelist_ids.includes(this.pricelist.id))) {
                continue;
            }
            if (program.trigger === "with_code") {
                if (!this._canGenerateRewards(program, totalWithTax, totalWithoutTax)) {
                    continue;
                }
            }
            if ((coupon_id && couponProgram.coupon_id !== coupon_id) || (program_id && couponProgram.program_id !== program_id)) {
                continue;
            }

            const points = this._getRealCouponPoints(couponProgram.coupon_id);

            for (const reward of program.rewards) {
                if (points < reward.required_points) {
                    continue;
                }
                if ((reward.program_id.program_type === 'coupons' && this.orderlines.find((line) => line.reward_id === reward.id))) {
                    continue;
                }
                if (auto && this.disabledRewards.has(reward.id)) {
                    continue;
                }
                if (reward.is_global_discount && reward.discount <= globalDiscountPercent) {
                    continue;
                }
                if (reward.reward_type === "discount" && totalIsZero) {
                    continue;
                }

                let unclaimedQty;

                // ✅ MULTI-APLICACIÓN DE REWARDS DE TIPO DISCOUNT
                if (reward.reward_type === "discount") {
                    const validProductIds = new Set(
                        reward.program_id.rules.flatMap(rule => rule.valid_product_ids || [])
                    );

                    if (!validProductIds.size) {
                        continue;
                    }

                    const matchingQty = this.orderlines
                        .filter(line => validProductIds.has(line.product.id))
                        .reduce((sum, line) => sum + line.quantity, 0);

                    const minQty = reward.program_id.rules[0].min_quantity || 1;
                    const applicableTimes = Math.floor(matchingQty / minQty);

                    if (applicableTimes <= 0) {
                        continue;
                    }

                    for (let i = 0; i < applicableTimes; i++) {
                        result.push({
                            coupon_id: couponProgram.coupon_id,
                            reward: reward,
                        });
                    }

                    continue; // Saltar el push original para evitar duplicados
                }

                // Lógica original para reward_type === "product"
                if (reward.reward_type === "product") {
                    if (!reward.multi_product) {
                        const product = this.pos.db.get_product_by_id(reward.reward_product_ids[0]);
                        if (!product) {
                            continue;
                        }
                        unclaimedQty = this._computeUnclaimedFreeProductQty(reward, couponProgram.coupon_id, product, points);
                    }
                    if (!unclaimedQty || unclaimedQty <= 0) {
                        continue;
                    }
                }

                result.push({
                    coupon_id: couponProgram.coupon_id,
                    reward: reward,
                    potentialQty: unclaimedQty,
                });
            }
        }

        console.log('Se aplicó el descuento según la promoción')

        return result;
    },
});
