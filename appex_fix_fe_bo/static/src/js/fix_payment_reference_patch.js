/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { jsonrpc } from "@web/core/network/rpc_service";
import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";

patch(PaymentScreen.prototype, {
    async IsPaymentReferenceButton() {
        console.log("[INFO] Iniciando interceptación de tarjeta...");

        const order = this.pos.get_order();
        if (!Array.isArray(this.pos.pos_payment_ref)) {
            this.pos.pos_payment_ref = [];
        }

        const lastRef = this.pos.pos_payment_ref[this.pos.pos_payment_ref.length - 1] || {};

        // Primeros 4 dígitos con restricción de solo números y max 4 caracteres
        const { confirmed: confirmedFirst, payload: firstInput } = await this.env.services.popup.add(TextInputPopup, {
            title: 'Primeros 4 dígitos de la tarjeta',
            placeholder: 'Ej: 1234',
        });

        if (!confirmedFirst || !firstInput) {
            console.warn("[WARN] No se confirmaron los primeros 4 dígitos. Cerrando PopUp.");
            return;
        }

        const first4 = (firstInput || '').replace(/\D/g, '').slice(0, 4);
        if (first4.length !== 4) {
            alert("Debes ingresar exactamente 4 dígitos.");
            return;
        }

        // Últimos 4 dígitos con la misma restricción
        const { confirmed: confirmedLast, payload: lastInput } = await this.env.services.popup.add(TextInputPopup, {
            title: 'Últimos 4 dígitos de la tarjeta',
            placeholder: 'Ej: 5678',
        });

        if (!confirmedLast || !lastInput) {
            console.warn("[WARN] No se confirmaron los últimos 4 dígitos. Cerrando PopUp.");
            return;
        }

        const last4 = (lastInput || '').replace(/\D/g, '').slice(-4);
        if (last4.length !== 4) {
            alert("Debes ingresar exactamente los últimos 4 dígitos.");
            return;
        }

        // Formato final
        const formattedCard = `${first4}00000000${last4}`;

        if (this.pos.pos_payment_ref.length > 0) {
            lastRef.card = formattedCard;
            lastRef.order = order.name;
        } else {
            this.pos.pos_payment_ref.push({ card: formattedCard, order: order.name });
        }

        await jsonrpc('/create_card', {
            name: order.name,
            card: formattedCard,
        });

        console.log("[INFO] Tarjeta guardada:", formattedCard);
    }
});
