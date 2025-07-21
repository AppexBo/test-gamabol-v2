/** @odoo-module **/

// import { patch } from "@web/core/utils/patch";
// import { TicketScreen } from "@point_of_sale/app/screens/ticket_screen/ticket_screen";
// import { jsonrpc } from "@web/core/network/rpc_service";
// import { registry } from "@web/core/registry";
// import { TextInputPopup } from "@point_of_sale/app/utils/input_popups/text_input_popup";

import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";
import { jsonrpc } from "@web/core/network/rpc_service";

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup() {
        super.setup(...arguments);
        // this.edi_state = false;
    },

    //@override
    // export_as_JSON() {
    //     const json = super.export_as_JSON(...arguments);
    //     if (json) {
    //         json.edi_state = this.edi_state;
    //     }
    //     return json;
    // },
    //@override
    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.codigoEstado = json.codigoEstado;
        this.edi_state = json.edi_state;
        
    },
});
