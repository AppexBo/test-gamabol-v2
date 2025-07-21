/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.observadorPOSparaPyD(this.pos);
	}, 

    observadorPOSparaPyD(pos){
        const observer_pyd = new MutationObserver(() => {
            this.ocultar_boton_precio_y_desc();
        });
        
        observer_pyd.observe(document.body, {
            childList: true,
            subtree: true
        });
    },

    ocultar_boton_precio_y_desc(){
        document.querySelectorAll('button.col.btn').forEach(btn => {
            const text = btn.textContent.trim();
            if (text === '% de desc.' || text === 'Precio') {
                btn.style.visibility = 'hidden';
                //btn.disabled = true;
                //console.log("bloquear");
            }
        });
    },

});