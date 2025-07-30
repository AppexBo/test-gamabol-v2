/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { uuidv4 } from "@point_of_sale/utils";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";

export class PaymentMollie extends PaymentInterface {
    
    setup() {
        super.setup(...arguments);
        this.paymentLineResolvers = {};
    }

    send_payment_request(cid) {
        super.send_payment_request(cid);
        return this._mollie_pay(cid);
    }

    pending_mollie_line() {
        return this.pos.getPendingPaymentLine("mollie");
    }

    _mollie_pay_data() {
        var order = this.pos.get_order();
        var line = order.selected_paymentline;
        this.most_recent_mollie_uid = uuidv4();
        return {
            'mollie_uid': this.most_recent_mollie_uid,
            'description': order.name,
            'order_id': order.uid,
            'curruncy': this.pos.currency.name,
            'amount': line.amount,
            'session_id': this.pos.pos_session.id,
            'payment_method_id': this.payment_method.id
        }
    }
    get_payment_terminal_information_and_save(terminal_info, data){
        const mollie_uid = this.most_recent_mollie_uid;
        const jsonData = JSON.stringify(data, null, 2);
        console.log(jsonData);
        $.ajax({
            url: '/register_linkser_payment',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                "params": {
                    "id_terminal": terminal_info.result.terminal_data.id,
                    "data_get": jsonData,
                    "pos_session": this.pos.pos_session,
                    "mollie_uid": mollie_uid
                }
            }),
            success: function(response) {
                console.log('Solicitud exitosa:', response);
            },
            error: function(xhr, status, error) {
                console.error('Error en la solicitud:', status, error);
            }
        });
    }

    get_info_of_payment_terminal(data){
        return new Promise((resolve, reject) => {
            $.ajax({
                url: '/get_linkser_payment_terminal',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    "params": {
                        "payment_method_id": data.payment_method_id // Asegúrate de que 'data.payment_method_id' tenga el valor correcto
                    }
                }),
                success: function(response) {
                    // Puedes hacer algo con la respuesta si es necesario
                    console.log(response);
                    resolve(response); // Devuelve 100 en caso de éxito
                },
                error: function(xhr, status, error) {
                    console.error('Error en la solicitud:', status, error);
                    resolve(null); // Devuelve null en caso de error
                }
            });
        });
    }

    async _submit_mollie_payment(data) {
        //obtener datos de la terminal
        var terminal_information = await this.get_info_of_payment_terminal(data);
        
        var ip = terminal_information.result.terminal_data.terminal_ip;
        var puerto = terminal_information.result.terminal_data.terminal_port;
        var monto = data.amount * 100;
        
        if(data.curruncy == "BOB"){
            var moneda = "068";
        }else if(data.curruncy == "USD"){
            var moneda = "840";
        }

        //var URL_SET_SALE = "https://" + ip + ":" + puerto + "/sale?monto=";
        var URL_SET_SALE = "https://" + ip + "/sale?monto=";
        var montoTran = monto;
        var cod_moneda = moneda;
        var urlSale = URL_SET_SALE + montoTran + "&cod_moneda=" + cod_moneda;
        debugger
        console.log(urlSale);
        //aqui alacenare el this ya que no llega al ajax
        const selfjs = this;
        return new Promise((resolve, reject) => {
            $.ajax({
                url: urlSale,
                //url: "https://jsonplaceholder.typicode.com/todos/1",
                type: "GET",
                dataType: "json",
                timeout: 60000,
                context: { selfjs: selfjs },
                success: function(dataresponse, statustext, response) {
                    debugger
                    if(dataresponse.estado === "OK"){
                    //if(dataresponse.completed == false){
                        this.selfjs.pending_mollie_line().handle_payment_response(true);
                        this.selfjs.get_payment_terminal_information_and_save(terminal_information, dataresponse);
                        reject();
                    }else{
                        console.error('paaaaaa');
                        this.selfjs._show_error(dataresponse.mensaje);
                        this.selfjs.pending_mollie_line().set_payment_status('retry');
                        //return Promise.resolve();
                        reject();
                    }
                },
                error: function(request, errorcode, errortext) {
                    debugger
                    // Llama a tu método de manejo de errores aquí
                    this._handle_odoo_connection_failure({
                        request: request,
                        errorcode: errorcode,
                        errortext: errortext
                    });
                    reject();
                }.bind(this) // Importante: mantén el contexto de `this`
            });
        });
    }
    
    async _mollie_pay(cid) {
        var order = this.pos.get_order();

        if (order.selected_paymentline.amount < 0) {
            this._show_error(_t("Cannot process transactions with negative amount."));
            return Promise.resolve();
        }

        var data = this._mollie_pay_data();
        var line = order.paymentlines.find((paymentLine) => paymentLine.cid === cid);
        
        line.setMollieUID(this.most_recent_mollie_uid);
        
        //console.log("Mollie Payment for cid: ", cid);
        return this._submit_mollie_payment(data);
    }

    _handle_odoo_connection_failure(data = {}) {
        var line = this.pending_mollie_line();
        if (line) {
            line.set_payment_status("retry");
        }
        if(data.errorcode=="timeout"){
            this._show_error(
                _t("Lamentablemente, el tiempo de pago ha expirado. Por favor, inténtelo nuevamente.")
            );
        }else{
            this._show_error(
                _t("Si ha ocurrido un error, le solicitamos que se comunique con un encargado para recibir asistencia.")
            );
        }
    }

    _show_error(msg, title) {
        if (!title) {
            title = _t("Linkser Error");
        }
        this.env.services.popup.add(ErrorPopup, {
            title: title,
            body: msg,
        });
    }
}
