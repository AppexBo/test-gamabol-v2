import logging
import json

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class MolliePosTerminal(models.Model):
    _name = 'mollie.pos.terminal.payments'
    _description = 'Mollie Pos Terminal'

    name = fields.Char("Transaction ID")
    mollie_uid = fields.Char("Linkser UID")
    terminal_id = fields.Many2one('mollie.pos.terminal')
    session_id = fields.Many2one('pos.session')
    mollie_latest_response = fields.Json('Response', default={})
    status = fields.Selection([
        ('paid', 'Paid'),
    ], default='paid')

    def _create_mollie_payment_request(self, id_terminal, data, pos_session, mollie_uid):
        # Contar el número de registros existentes para generar un nuevo ID único
        transaction_count = self.search_count([])
        new_transaction_id = transaction_count + 1  # Correlativo

        _logger.info("Creando registro de pago con: %s", {
            'name': str(new_transaction_id),
            'mollie_uid': mollie_uid,
            'terminal_id': id_terminal,
            'session_id': pos_session,
            'status': 'paid',
        })

        # Crear el registro
        payment_record = self.create({
            'name': str(new_transaction_id),  # Conversión a cadena
            'mollie_uid': mollie_uid,  # Vacío si no hay mollie_uid
            'terminal_id': id_terminal,
            'session_id': pos_session.get('id') if pos_session else None,  # Solo pasar el ID
            'mollie_latest_response': data,
            'status': 'paid',  # Siempre 'paid'
        })
        
        result = {
            'message': "se registro el pago"
        }
        return result
        

    #@api.model
    def get_mollie_payment_status(self, transaction_id=None, mollie_uid=None):
        domain = []
        if transaction_id:
            domain.append(('name', '=', transaction_id))
        elif mollie_uid:
            domain.append(('mollie_uid', '=', mollie_uid))
        else:
            return {}
        mollie_payment = self.search(domain, limit=1)
        if mollie_payment:
            return mollie_payment.mollie_latest_response
        return {}