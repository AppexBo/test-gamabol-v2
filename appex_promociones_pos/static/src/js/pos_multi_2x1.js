/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

// Interceptamos el momento en que se procesan los datos de lealtad
patch(PosStore.prototype, {
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
