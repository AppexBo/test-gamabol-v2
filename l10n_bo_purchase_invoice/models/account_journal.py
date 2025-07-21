# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError

class AccountJournal(models.Model):
    _inherit = ['account.journal']
    

    
    bo_purchase_edi = fields.Boolean(
        string='Facturas compras (BO)',
    )
    

    
    adm_journal_bo_purchase_edi = fields.Boolean(
        string='Administrador de compras (BO)',
        compute='_compute_adm_journal_bo_purchase_edi' 
    )
    
    def is_purchase_edi_user(self) -> bool:
        for record in self:
            group = record.env.ref('l10n_bo_purchase_invoice.group_adm_purchase_edi')
            return True if group and record.env.user in group.users else False    
        
    
    @api.depends('bo_purchase_edi')
    def _compute_adm_journal_bo_purchase_edi(self):
        for record in self:
            record.adm_journal_bo_purchase_edi = record.is_purchase_edi_user()    
    
    
    @api.onchange('bo_edi')
    def _onchange_bo_edi(self):
        if not self.is_purchase_edi_user():
            raise UserError('Necesita permisos de ADMINISTADOR (BO) para editar la configuración del diario')
        
    
    
    purchase_sequence = fields.Integer(
        string='Secuencia de compras (BO)',
        copy=False
    )
    
    def get_purchase_sequence(self):
        if self.bo_purchase_edi:
            return self.purchase_sequence + 1
        raise UserError('Diario de compras no habilitado para secuencia de compras (BO)')
    

    def next_purchase_sequence(self):
        if self.bo_purchase_edi:
            self.write({'purchase_sequence' : self.purchase_sequence + 1})
        else:
            raise UserError('Diario de compras no habilitado para secuencia de compras (BO)')
    
        
            

    
    auto_confirm_bo_purchase_edi = fields.Boolean(
        string='Confirmación automática de compras (BO)',
        help='Al confirmar la factura de proveedor se genera un xml y se envian el paquete compuesto de 1 factura.'
    )
    