from odoo import models, api, fields

import logging

_logger = logging.getLogger(__name__)

class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    @api.model
    def create(self, vals):
        order = self.env['pos.order'].search([('id', '=', vals.get('order_id'))], limit=1)
        #para lectura del contenido de orer
        #if order:
        #    order_data = order.read()[0]  # Get all fields as a dictionary
        #    _logger.info("POS Order data: %s", order_data)
        #else:
        #    _logger.info("No POS Order found with id %s", vals.get('order_id'))
        if order and not(order.to_invoice):
            #_logger.info("Data de la line de orden: %s", vals)
            vals['tax_ids'] = [[6, False, []]]
            #_logger.info("Data de la line de orden: %s", vals)

        return super(PosOrderLine, self).create(vals)