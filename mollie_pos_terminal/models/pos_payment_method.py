import base64

from odoo import fields, models, api
from odoo.tools import file_open


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    mollie_pos_terminal_id = fields.Many2one('mollie.pos.terminal', string='Linkser Pos Terminal', domain="[('status', '=', 'active')]")
    mollie_latest_response = fields.Json('History', default={})
    mollie_payment_default_partner = fields.Many2one('res.partner')

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('mollie', 'Linkser')]

    def mollie_payment_request(self, data):
        self.sudo().mollie_latest_response = {}  # avoid handling old responses multiple times
        return

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            if not val.get('image') and val.get('use_payment_terminal') == 'mollie':
                mollie_image = file_open('mollie_pos_terminal/static/src/img/logo-linkser.png', mode='rb').read()
                if mollie_image:
                    val['image'] = base64.b64encode(mollie_image)
        return super().create(vals_list)

    def custom_method(self, id_terminal , data, pos_session, mollie_uid):
        termianl = self.env['mollie.pos.terminal'].browse(id_terminal)
        return termianl.sudo()._register_transaction(data, pos_session, mollie_uid)

    def get_information(self, payment_method_id):
        payment_method = self.sudo().browse(payment_method_id)
        if payment_method.exists():
            terminal_model = self.env['mollie.pos.terminal']
            #return payment_method.id
            terminal = terminal_model.sudo().get_terminal_information(payment_method.mollie_pos_terminal_id)
            return terminal
        else:
            return None  # O lanza una excepción si prefieres
        