class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'
    
    @api.model
    def create(self, vals):
        order = self.env['pos.order'].search([('id', '=', vals.get('orden_id'))], limit=1)
        if order and order.is_invoiced:
            _logger.info("CREATING PosOrderLine with values: %s", vals)
        return super(PosOrderLine, self).create(vals)