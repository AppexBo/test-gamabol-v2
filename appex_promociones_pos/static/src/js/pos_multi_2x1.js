/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Order } from "@point_of_sale/app/store/models";

patch(Order.prototype, {
    _applyReward(reward, couponId, args) {
        console.log("Se aplicó una recompensa:");
        console.log("Tipo:", reward.reward_type);
        console.log("Producto relacionado:", args.product);
        console.log("Precio:", args.price);
        console.log("Cantidad:", args.quantity);
        console.log("Puntos usados:", args.cost);

        // Llama a la función original
        return super._applyReward(reward, couponId, args);
    }
});
