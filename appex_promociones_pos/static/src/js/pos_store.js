/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    async _processData(loadedData) {
        await super._processData(...arguments);
        console.log("Recompensas cargadas:", loadedData['loyalty.program']);

        // Opcionalmente podrías verificar aquí los valores
        const programs = loadedData['loyalty.program'];
        for (const prog of programs) {
            for (const reward of prog.rewards || []) {
                console.log(`Reward ${reward.id} apply_multiple: `, reward.apply_multiple);
            }
        }
    },
});
