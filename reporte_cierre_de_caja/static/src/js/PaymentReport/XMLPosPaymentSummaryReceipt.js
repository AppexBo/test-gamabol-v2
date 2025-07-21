/** @odoo-module */

import { usePos } from "@point_of_sale/app/store/pos_hook";
import {Component } from "@odoo/owl";

export class XMLPosPaymentSummaryReceipt extends Component {
    static template = "reporte_cierre_de_caja.XMLPosPaymentSummaryReceipt";
    
    setup() {
        this.pos = usePos();
        
    }
    
}

