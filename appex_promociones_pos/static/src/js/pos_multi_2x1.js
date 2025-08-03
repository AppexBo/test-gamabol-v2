/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models/order";

// Interceptamos la búsqueda de recompensas aplicables
patch(Order.prototype, {
    getPotentialDiscountRewards() {
        const rewards = super.getPotentialDiscountRewards();

        if (rewards?.length) {
            for (const reward of rewards) {
                console.log(' Se encontró una recompensa aplicable:', reward.name);
                console.log(' Tipo de recompensa:', reward.reward_type);
                console.log(' Monto del descuento:', reward.discount || 0);

                // Verificamos si es 2x1 basado en cantidad mínima
                for (const rule of reward.program_id.rules) {
                    if (rule.min_quantity >= 2) {
                        console.log(` Regla cumplida: mínimo ${rule.min_quantity} productos`);
                    }
                }
            }
        }

        return rewards;
    },
});
