/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";
import { _t } from "@web/core/l10n/translation";


// Parchea Order para aplicar descuentos múltiples si la regla lo permite
patch(Order.prototype, {


    _getRewardLineValuesDiscount(args) {
        function _newRandomRewardCode() {
            return (Math.random() + 1).toString(36).substring(3);
        }

        function getDiscountableOnMultiple(reward) {
            const MIN_QTY = 2; // mínima cantidad para aplicar promoción
            const validProductIds = reward.all_discount_product_ids;
            const orderLines = this.get_orderlines();
            const linesToDiscount = [];

            for (const line of orderLines) {
                if (!line.get_quantity() || !line.price || line.reward_id) {
                    continue;
                }
                const product_id = line.comboParent?.product.id || line.get_product().id;

                if (validProductIds.has(product_id)) {
                    linesToDiscount.push(line);
                }
            }

            let totalDiscount = 0;
            const discountablePerTax = {};

            for (const line of linesToDiscount) {
                const qty = line.get_quantity();
                const unitPrice = line.get_unit_price();
                const discountSets = Math.floor(qty / MIN_QTY); // cuántos pares hay

                if (discountSets > 0) {
                    const discountAmount = discountSets * unitPrice; // uno gratis por cada par
                    totalDiscount += discountAmount;

                    const taxKey = line.get_taxes().map((t) => t.id);
                    if (!discountablePerTax[taxKey]) {
                        discountablePerTax[taxKey] = 0;
                    }
                    discountablePerTax[taxKey] += discountAmount;
                }
            }

            return {
                discountable: totalDiscount,
                discountablePerTax: discountablePerTax,
            };
        };

        const reward = args["reward"];
        const coupon_id = args["coupon_id"];



        const rewardAppliesTo = reward.discount_applicability;
        let getDiscountable;
        const rules = reward.program_id.rules || [];

        console.log("las reglas son: ", rules )
        // Detectar si alguna regla tiene apply_multiple
        const useMultiple = reward.apply_multiple;
        console.log("La recompensa está con useMultiple: ", useMultiple)

        if (useMultiple) {
            console.log('Se aplicó useMultiple')
            getDiscountable = getDiscountableOnMultiple.bind(this);
        } else if (rewardAppliesTo === "order") {
            getDiscountable = this._getDiscountableOnOrder.bind(this);
        } else if (rewardAppliesTo === "cheapest") {
            getDiscountable = this._getDiscountableOnCheapest.bind(this);
        } else if (rewardAppliesTo === "specific") {
            getDiscountable = this._getDiscountableOnSpecific.bind(this);
        }
        if (!getDiscountable) {
            return _t("Unknown discount type");
        }
        let {
            discountable,
            discountablePerTax
        } = getDiscountable(reward);
        discountable = Math.min(this.get_total_with_tax(), discountable);
        if (!discountable) {
            return [];
        }
        let maxDiscount = reward.discount_max_amount || Infinity;
        if (reward.discount_mode === "per_point") {
            const points = (["ewallet", "gift_card"].includes(reward.program_id.program_type)) ? this._getRealCouponPoints(coupon_id) : Math.floor(this._getRealCouponPoints(coupon_id) / reward.required_points) * reward.required_points;
            maxDiscount = Math.min(maxDiscount, reward.discount * points);
        } else if (reward.discount_mode === "per_order") {
            maxDiscount = Math.min(maxDiscount, reward.discount);
        } else if (reward.discount_mode === "percent") {
            maxDiscount = Math.min(maxDiscount, discountable * (reward.discount / 100));
        }
        const rewardCode = _newRandomRewardCode();
        let pointCost = reward.clear_wallet ? this._getRealCouponPoints(coupon_id) : reward.required_points;
        if (reward.discount_mode === "per_point" && !reward.clear_wallet) {
            pointCost = Math.min(maxDiscount, discountable) / reward.discount;
        }
        const discountProduct = reward.discount_line_product_id;
        if (["ewallet", "gift_card"].includes(reward.program_id.program_type)) {
            const taxes_to_apply = discountProduct.taxes_id.map((id) => {
                return {
                    ...this.pos.taxes_by_id[id],
                    price_include: true
                };
            });
            const tax_res = this.pos.compute_all(taxes_to_apply, -Math.min(maxDiscount, discountable), 1, this.pos.currency.rounding);
            let new_price = tax_res["total_excluded"];
            new_price += tax_res.taxes.filter((tax) => this.pos.taxes_by_id[tax.id].price_include).reduce((sum, tax) => (sum += tax.amount), 0);
            return [{
                product: discountProduct,
                price: new_price,
                quantity: 1,
                reward_id: reward.id,
                is_reward_line: true,
                coupon_id: coupon_id,
                points_cost: pointCost,
                reward_identifier_code: rewardCode,
                merge: false,
                taxIds: discountProduct.taxes_id,
            },];
        }
        const discountFactor = discountable ? Math.min(1, maxDiscount / discountable) : 1;
        const result = Object.entries(discountablePerTax).reduce((lst, entry) => {
            if (!entry[1]) {
                return lst;
            }
            const taxIds = entry[0] === "" ? [] : entry[0].split(",").map((str) => parseInt(str));
            lst.push({
                product: discountProduct,
                price: -(entry[1] * discountFactor),
                quantity: 1,
                reward_id: reward.id,
                is_reward_line: true,
                coupon_id: coupon_id,
                points_cost: 0,
                reward_identifier_code: rewardCode,
                tax_ids: taxIds,
                merge: false,
            });
            return lst;
        }, []);
        if (result.length) {
            result[0]["points_cost"] = pointCost;
        }
        console.log('Se está usando _getRewardLineValuesDiscount: ', result)
        return result;
    },


});
