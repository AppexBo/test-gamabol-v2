# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
class IrAttachment(models.Model):
    _inherit = ['ir.attachment']
    
    
    tax_document = fields.Boolean(
        string='Documento fiscal',
        copy=False,
        readonly=True 
    )
    
    
    def unlink(self):
        for record in self:
            if record.tax_document:
                raise UserError(
                    'No puede eliminar un documento fiscal.'
                )
        return super(IrAttachment, self).unlink()
    