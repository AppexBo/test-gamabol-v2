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
            const applicableProducts = reward.all_discount_product_ids;
            const remainingAmountPerLine = {};
            const discountableLines = [];

            // Recopilar todas las líneas aplicables
            for (const line of this.get_orderlines()) {
                if (!line.get_quantity() || !line.price) continue;

                const product_id = line.comboParent?.product.id || line.get_product().id;

                if (applicableProducts.has(product_id)) {
                    const unit_price = line.get_price_with_tax() / line.get_quantity();

                    for (let i = 0; i < line.get_quantity(); i++) {
                        discountableLines.push({
                            line,
                            unit_price,
                            cid: line.cid,
                        });
                    }

                    remainingAmountPerLine[line.cid] = line.get_price_with_tax();
                }
            }

            // Ordenar por precio de menor a mayor
            discountableLines.sort((a, b) => a.unit_price - b.unit_price);

            // Agrupar de a 2 y regalar el más barato
            let discountable = 0;
            const discountablePerTax = {};

            for (let i = 0; i + 1 < discountableLines.length; i += 2) {
                const [cheapest, _] = [discountableLines[i], discountableLines[i + 1]];

                discountable += cheapest.unit_price;

                const taxKey = cheapest.line.get_taxes().map(t => t.id);
                if (!discountablePerTax[taxKey]) {
                    discountablePerTax[taxKey] = 0;
                }

                discountablePerTax[taxKey] += cheapest.line.get_base_price() * (cheapest.unit_price / cheapest.line.get_price_with_tax());
            }

            return {
                discountable,
                discountablePerTax
            };
        };

        const reward = args["reward"];
        const coupon_id = args["coupon_id"];



        const rewardAppliesTo = reward.discount_applicability;
        let getDiscountable;
        const rules = reward.program_id.rules || [];

        // Detectar si alguna regla tiene apply_multiple
        const useMultiple = true;

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
