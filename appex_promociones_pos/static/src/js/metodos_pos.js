/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

patch(Order.prototype, {

    async addProductFromUi(product, options) {
        const order = this.get_order();
        const linkedProgramIds = this.productId2ProgramIds[product.id] || [];
        const linkedPrograms = linkedProgramIds.map((id) => this.program_by_id[id]);
        let selectedProgram = null;
        if (linkedPrograms.length > 1) {
            const {
                confirmed,
                payload: program
            } = await this.popup.add(SelectionPopup, {
                title: _t("Select program"),
                list: linkedPrograms.map((program) => ({
                    id: program.id,
                    item: program,
                    label: program.name,
                })),
            });
            if (confirmed) {
                selectedProgram = program;
            } else {
                return;
            }
        } else if (linkedPrograms.length === 1) {
            selectedProgram = linkedPrograms[0];
        }
        const orderTotal = this.get_order().get_total_with_tax();
        if (selectedProgram && ["gift_card", "ewallet"].includes(selectedProgram.program_type) && orderTotal < 0) {
            options.price = -orderTotal;
        }
        if (selectedProgram && selectedProgram.program_type == "gift_card") {
            const shouldProceed = await this._setupGiftCardOptions(selectedProgram, options);
            if (!shouldProceed) {
                return;
            }
        } else if (selectedProgram && selectedProgram.program_type == "ewallet") {
            const shouldProceed = await this.setupEWalletOptions(selectedProgram, options);
            if (!shouldProceed) {
                return;
            }
        }
        const potentialRewards = this.getPotentialFreeProductRewards();
        const rewardsToApply = [];
        for (const reward of potentialRewards) {
            for (const reward_product_id of reward.reward.reward_product_ids) {
                if (reward_product_id == product.id) {
                    rewardsToApply.push(reward);
                }
            }
        }
        await super.addProductFromUi(product, options);
        await order._updatePrograms();
        if (rewardsToApply.length == 1) {
            const reward = rewardsToApply[0];
            order._applyReward(reward.reward, reward.coupon_id, {
                product: product.id
            });
        }
        order._updateRewards();
        return options;
    },

    async _updateLoyaltyPrograms() {
        await this._checkMissingCoupons();
        await this._updatePrograms();
    },

    _updateRewards() {
        if (this.pos.programs.length === 0) {
            return;
        }
        updateRewardsMutex.exec(() => {
            return this._updateLoyaltyPrograms().then(async () => {
                const claimableRewards = this.getClaimableRewards(false, false, true);
                for (const {
                    coupon_id,
                    reward
                }
                    of claimableRewards) {
                    if (reward.program_id.rewards.length === 1 && !reward.program_id.is_nominative && (reward.reward_type !== "product" || (reward.reward_type == "product" && !reward.multi_product))) {
                        this._applyReward(reward, coupon_id);
                    }
                }
                this._updateRewardLines();
                await this._updateLoyaltyPrograms();
            });
        });
    },

    _get_reward_lines() {
        if (this.orderlines) {
            return this.orderlines.filter((line) => line.is_reward_line);
        }
        return this.orderlines;
    },

    _updateRewardLines() {
        if (!this.orderlines.length) {
            return;
        }
        const rewardLines = this._get_reward_lines();
        if (!rewardLines.length) {
            return;
        }
        const productRewards = [];
        const otherRewards = [];
        const paymentRewards = [];
        for (const line of rewardLines) {
            const claimedReward = {
                reward: this.pos.reward_by_id[line.reward_id],
                coupon_id: line.coupon_id,
                args: {
                    product: line.reward_product_id,
                    price: line.price,
                    quantity: line.quantity,
                    cost: line.points_cost,
                },
                reward_identifier_code: line.reward_identifier_code,
            };
            if (claimedReward.reward.program_id.program_type === "gift_card" || claimedReward.reward.program_id.program_type === "ewallet") {
                paymentRewards.push(claimedReward);
            } else if (claimedReward.reward.reward_type === "product") {
                productRewards.push(claimedReward);
            } else if (!otherRewards.some((reward) => reward.reward_identifier_code === claimedReward.reward_identifier_code)) {
                otherRewards.push(claimedReward);
            }
            this.orderlines.remove(line);
        }
        const allRewards = productRewards.concat(otherRewards).concat(paymentRewards);
        const allRewardsMerged = [];
        allRewards.forEach((reward) => {
            if (reward.reward.reward_type == "discount") {
                allRewardsMerged.push(reward);
            } else {
                const reward_index = allRewardsMerged.findIndex((item) => item.reward.id === reward.reward.id && item.args.price === reward.args.price);
                if (reward_index > -1) {
                    allRewardsMerged[reward_index].args.quantity += reward.args.quantity;
                    allRewardsMerged[reward_index].args.cost += reward.args.cost;
                } else {
                    allRewardsMerged.push(reward);
                }
            }
        });
        for (const claimedReward of allRewardsMerged) {
            if (!this.codeActivatedCoupons.find((coupon) => coupon.id === claimedReward.coupon_id) && !this.couponPointChanges[claimedReward.coupon_id]) {
                continue;
            }
            if (claimedReward.reward.reward_product_ids?.length === 1) {
                delete claimedReward.args["quantity"];
            }
            this._applyReward(claimedReward.reward, claimedReward.coupon_id, claimedReward.args);
        }
    },

    async _applyReward(reward, coupon_id, potentialQty) {
        const order = this.pos.get_order();
        order.disabledRewards.delete(reward.id);
        const args = {};
        if (reward.reward_type === "product" && reward.multi_product) {
            const productsList = reward.reward_product_ids.map((product_id) => ({
                id: product_id,
                label: this.pos.db.get_product_by_id(product_id).display_name,
                item: product_id,
            }));
            const {
                confirmed,
                payload: selectedProduct
            } = await this.popup.add(SelectionPopup, {
                title: _t("Please select a product for this reward"),
                list: productsList,
            });
            if (!confirmed) {
                return false;
            }
            args["product"] = selectedProduct;
        }
        if ((reward.reward_type == "product" && reward.program_id.applies_on !== "both") || (reward.program_id.applies_on == "both" && potentialQty)) {
            this.pos.addProductToCurrentOrder(args["product"] || reward.reward_product_ids[0], {
                quantity: potentialQty || 1
            });
            return true;
        } else {
            const result = order._applyReward(reward, coupon_id, args);
            if (result !== true) {
                this.notification.add(result);
            }
            order._updateRewards();
            return result;
        }
    },

    _applyReward(reward, coupon_id, args) {
        if (this._getRealCouponPoints(coupon_id) < reward.required_points) {
            return _t("There are not enough points on the coupon to claim this reward.");
        }
        if (reward.is_global_discount) {
            const globalDiscountLines = this._getGlobalDiscountLines();
            if (globalDiscountLines.length) {
                const rewardId = globalDiscountLines[0].reward_id;
                if (rewardId != reward.id && this.pos.reward_by_id[rewardId].discount >= reward.discount) {
                    return _t("A better global discount is already applied.");
                } else if (rewardId != rewardId.id) {
                    for (const line of globalDiscountLines) {
                        this.orderlines.remove(line);
                    }
                }
            }
        }
        args = args || {};
        const rewardLines = this._getRewardLineValues({
            reward: reward,
            coupon_id: coupon_id,
            product: args["product"] || null,
            price: args["price"] || null,
            quantity: args["quantity"] || null,
            cost: args["cost"] || null,
        });
        if (!Array.isArray(rewardLines)) {
            return rewardLines;
        }
        if (!rewardLines.length) {
            return _t("The reward could not be applied.");
        }
        for (const rewardLine of rewardLines) {
            this.orderlines.add(this._createLineFromVals(rewardLine));
        }
        return true;
    },
    _getRewardLineValues(args) {
        const reward = args["reward"];
        if (reward.reward_type === "discount") {
            return this._getRewardLineValuesDiscount(args);
        } else if (reward.reward_type === "product") {
            return this._getRewardLineValuesProduct(args);
        }
        return [];
    },

    _getRewardLineValuesDiscount(args) {
        const reward = args["reward"];
        const coupon_id = args["coupon_id"];
        const rewardAppliesTo = reward.discount_applicability;
        let getDiscountable;
        if (rewardAppliesTo === "order") {
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
        return result;
    },
});
