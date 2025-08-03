/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

// Parchea Order para aplicar descuentos múltiples si la regla lo permite
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
            if (!program) continue;

            if (program.pricelist_ids.length > 0 && (!this.pricelist || !program.pricelist_ids.includes(this.pricelist.id))) {
                continue;
            }
            if (program.trigger == "with_code") {
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
                if ((reward.program_id.program_type === 'coupons' && this.orderlines.find(line => line.reward_id === reward.id))) {
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

                // Aplicación múltiple de producto
                if (reward.reward_type === "product") {
                    const validProductIds = new Set();
                    reward.program_id.rules.forEach(rule => {
                        if (rule.any_product) {
                            // Si se permite cualquier producto, se ignora el filtro
                            validProductIds.clear(); 
                        } else {
                            rule.valid_product_ids.forEach(pid => validProductIds.add(pid));
                        }
                    });

                    // Si validProductIds no está vacío, filtrar por esos productos
                    let matchingLines = this.orderlines.filter(line => {
                        return !line.reward_id && (!validProductIds.size || validProductIds.has(line.product.id));
                    });

                    // Cantidad de productos que se pueden premiar
                    let qtyToReward = matchingLines.reduce((sum, line) => sum + line.quantity, 0);

                    if (!qtyToReward || qtyToReward <= 0) {
                        continue;
                    }

                    const canApplyMultiple = reward.program_id.rules.some(rule => rule.apply_multiple);
                    const qtyRewardable = canApplyMultiple ? Math.floor(points / reward.required_points) : 1;
                    const finalQty = Math.min(qtyToReward, qtyRewardable);

                    if (finalQty <= 0) continue;

                    result.push({
                        coupon_id: couponProgram.coupon_id,
                        reward: reward,
                        potentialQty: finalQty,
                    });
                } else {
                    // Otro tipo de recompensa (descuento, porcentaje, etc.)
                    result.push({
                        coupon_id: couponProgram.coupon_id,
                        reward: reward,
                    });
                }
            }
        }

        console.log("Promociones encontradas:", result);
        return result;
    },
});
