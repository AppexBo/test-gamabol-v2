/** @odoo-module **/

import { useService } from "@web/core/utils/hooks";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";
import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
import { patch } from "@web/core/utils/patch";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";

patch(TicketScreen.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
    },

    async onL10nBoCancelInovice(order) {
        console.log(order);

        const selectionList = this.pos.cancellation_reason_list.filter((c) =>
            [1, 3].includes(c.codigoClasificador)
        );
        
        console.log(selectionList);

        const { confirmed, payload: reazon_id } = await this.popup.add(SelectionPopup, {
            title: _t("Anular factura"),
            list: selectionList.map((reason) => ({
                id: reason.id,
                item: reason,
                label: reason.name,
            })),
        });

        if (confirmed && reazon_id?.id) {
            console.log("Razón seleccionada:", reazon_id.id);
            try {
                await this.orm.silent.call(
                    "pos.order",
                    "action_l10n_bo_cancel_invoice",
                    [order.backendId],
                    {
                        context: {
                            cancel_reason_id: reazon_id.id,
                            move_id: order.account_move,
                        }
                    }
                );
                window.location.reload();
            } catch (error) {
                console.error("Error al anular la factura:", error);
                await this.popup.add(ConfirmPopup, {
                    title: _t("Error al anular"),
                    body: _t("No se pudo anular la factura. Verifique su conexión o intente más tarde."),
                });
            }
        }
    }
});
