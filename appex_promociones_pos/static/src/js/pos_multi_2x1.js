/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { LoyaltyLoader } from "@point_of_sale/app/models/loyalty_program/loyalty_program_loader";

// Interceptamos el momento en que se procesan los datos de lealtad
patch(LoyaltyLoader.prototype, {
    _loadLoyaltyData() {
        const result = super._loadLoyaltyData();

        // Buscamos si hay recompensas de tipo descuento
        for (const reward of this.rewards || []) {
            if (reward.reward_type === 'discount') {
                console.log('Hola mundo, se aplicó el descuento');
            }
        }

        return result;
    },
});
