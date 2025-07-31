from odoo import models, api, fields

import logging

_logger = logging.getLogger(__name__)

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    @api.model
    def create(self, vals):
        _logger.info("DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA: %s", vals)
        order = self.env['pos.order'].search([('id', '=', vals.get('order_id'))], limit=1)
        if order and order.is_invoiced:
            _logger.info("CREATING PosOrderLine with values: %s", vals)
        return super(PosOrderLine, self).create(vals)