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
        if order:
            order_data = order.read()[0]  # Get all fields as a dictionary
            self._logger.info("POS Order data: %s", order_data)
        else:
            self._logger.info("No POS Order found with id %s", vals.get('order_id'))
        if order and order.to_invoiced:
            _logger.info("CREATING PosOrderLine with values: %s", vals)
        return super(PosOrderLine, self).create(vals)