/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    async _updateRewards() {
        if (this.pos.programs.length === 0) {
            return;
        }

        console.log("🔁 Ejecutando _updateRewards (custom)");

        await updateRewardsMutex.exec(async () => {
            await this._updateLoyaltyPrograms();

            const claimableRewards = this.getClaimableRewards(false, false, true);

            for (const { coupon_id, reward } of claimableRewards) {
                // Personalizamos aquí para aplicar múltiples veces si corresponde
                if (
                    reward.program_id.rewards.length === 1 &&
                    !reward.program_id.is_nominative &&
                    (reward.reward_type !== "product" || (reward.reward_type === "product" && !reward.multi_product))
                ) {
                    console.log("🎯 Se aplica recompensa:", reward.name);
                    this._applyReward(reward, coupon_id);
                }
            }

            this._updateRewardLines();
            await this._updateLoyaltyPrograms();
        });
    },
});
