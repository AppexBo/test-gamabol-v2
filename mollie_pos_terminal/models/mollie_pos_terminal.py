import logging
import requests

import pdb

from werkzeug import urls

from odoo import fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class MolliePosTerminal(models.Model):
    _name = 'mollie.pos.terminal'
    _description = 'Mollie Pos Terminal'

    name = fields.Char()
    terminal_id = fields.Char('Terminal ID')
    terminal_ip = fields.Char('Terminal IP')
    terminal_port = fields.Char('Terminal PORT')
    comercio = fields.Char('Comercio')
    status = fields.Selection([
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ])
    currency_id = fields.Many2one('res.currency', string='Currency')
    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company)
    
    def show_form_and_tree(self):
        action = self.env['ir.actions.actions']._for_xml_id('mollie_pos_terminal.mollie_pos_terminal_payments_action')
        action.update({
            'domain': [('terminal_id', '=', self.id)],
            'views': [(self.env.ref('mollie_pos_terminal.mollie_pos_terminal_payments_view_tree').id, 'tree'), (self.env.ref('mollie_pos_terminal.mollie_pos_terminal_payments_view_form').id, 'form')],
            'res_id': self.id,
        })
        return action


    def _register_transaction(self, data, pos_session, mollie_uid):
        self_id = self.id
        terminal_payment_model = self.env['mollie.pos.terminal.payments']
        return terminal_payment_model.sudo()._create_mollie_payment_request(self_id, data, pos_session, mollie_uid)


    def get_terminal_information(self, terminalinfo):
        if terminalinfo.exists():
            return {
                'id': terminalinfo.id,
                'name': terminalinfo.name,
                'terminal_id': terminalinfo.terminal_id,
                'terminal_ip': terminalinfo.terminal_ip,
                'terminal_port': terminalinfo.terminal_port,
                'comercio': terminalinfo.comercio,
                'status': terminalinfo.status,
                'currency_id': terminalinfo.currency_id.id if terminalinfo.currency_id else None,
                'company_id': terminalinfo.company_id.id,
            }
        else:
            return None  # O lanza una excepción si prefieres