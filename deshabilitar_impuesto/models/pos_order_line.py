from odoo import models, api, fields

import logging

_logger = logging.getLogger(__name__)

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    @api.model
    def create(self, vals):
        _logger.info("DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA: %s", vals)
        order = self.env['pos.order'].search([('id', '=', vals.get('order_id'))], limit=1)
        _logger.info("DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA: %s", order)
        _logger.info("DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA: %s", order.is_invoiced)
        _logger.info("DATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA: %s", order.to_invoiced)
        if order and order.to_invoiced:
            _logger.info("CREATING PosOrderLine with values: %s", vals)
        return super(PosOrderLine, self).create(vals)