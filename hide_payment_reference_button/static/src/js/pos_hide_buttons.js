/** @odoo-module */

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        this.observadorPOS(this.pos);
	}, 

    observadorPOS(pos){
        const observer = new MutationObserver(() => {
            this.ocultar_payment_reference_button();
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },

    ocultar_payment_reference_button(){
        const paymentButton = document.getElementById('payment_reference_button');
        if (paymentButton) {
            // Subir hasta el elemento button padre y ocultarlo
            const buttonParent = paymentButton.closest('button');
            if (buttonParent) {
                buttonParent.style.display = 'none'; // Elimina completamente el espacio
            }
        }
    },

});