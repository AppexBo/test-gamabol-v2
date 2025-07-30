# coding: utf-8
import logging
import json
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PosMollieController(http.Controller):

    @http.route('/register_linkser_payment', type='json', auth='public', methods=['POST'])
    def register_linkser_payment(self, **post):
        data = post.get('data_get')
        mollie_uid = post.get('mollie_uid')

        terminal_id = post.get('id_terminal')
        pos_session = post.get('pos_session')
        # Llama al método custom_method del modelo pos.payment.method
        pos_payment_method_model = request.env['pos.payment.method']
        result = pos_payment_method_model.custom_method(terminal_id, data, pos_session, mollie_uid)
        return result

    @http.route('/get_linkser_payment_terminal', type='json', auth='public', methods=['POST'])
    def get_linkser_payment_terminal(self, **post):
        payment_method_id = post.get('payment_method_id')
        
        if payment_method_id is None:
            return {'status': 'error', 'message': 'payment_method_id is required'}
        else: 
            terminal = request.env['pos.payment.method']
            terminal_data = terminal.sudo().get_information(payment_method_id)
            # Aquí puedes hacer lo que necesites con payment_method_id
            return {'status': 'success', 'terminal_data': terminal_data}
