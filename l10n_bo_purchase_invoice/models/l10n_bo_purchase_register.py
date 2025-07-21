# -*- coding:utf-8 -*-

from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)



class L10nBoPurchaseRegister(models.Model):
    _name='l10n.bo.purchase.register'
    _description="Registro de compra (BO)"

    
    name = fields.Char(
        string='Nombre',
        readonly=True 
    )
    
    
    date_from = fields.Date(
        string='Desde',
    )
    
    date_to = fields.Date(
        string='Hasta',
    )
    
    
    purchase_register_line_ids = fields.One2many(
        string='Lineas de registro de compra',
        comodel_name='l10n.bo.purchase.register.line',
        inverse_name='purchase_register_id',
    )
    
    def get_preview_registers(self, PARAMS : list = []):
        #PARAMS.append(('invoice_id.bo_purchase_edi_anuled','=',False))
        PARAMS.append(('invoice_id.bo_purchase_edi_validated','=',True))
        
        l10n_bo_standard_rv_ids =  self.env['l10n.bo.purchase.register.line'].search(PARAMS)
        for l10n_bo_standard_rv_id in l10n_bo_standard_rv_ids:
            l10n_bo_standard_rv_id.write({'purchase_register_id': self.id})
    
    def get_invoice_ids(self):
        PARAMS = [
            ('move_type','=','in_invoice'),
            ('state','=','posted'),
            ('bo_purchase_edi_validated','=',True),
            #('bo_purchase_edi_anuled','=',False),
            ('bo_purchase_edi','=',True),
        ]
        preview_params = []
        if self.date_from and self.date_to:
            PARAMS.append(('invoice_date_edi','>=', self.date_from))
            PARAMS.append(('invoice_date_edi','<=', self.date_to))
            preview_params = [('dui_dim_date','>=', self.date_from), ('dui_dim_date','<=', self.date_to)]
        
        self.get_preview_registers(preview_params)
        
            
        return self.env['account.move'].search(
            PARAMS,
            order='invoice_date_edi desc'
        )
    
    def create_invoice_records(self, invoice_ids):
        new_l10n_bo_rv_records = []
        for invoice_id in invoice_ids:
            params = {
                'invoice_id'    :  invoice_id.id,
                'name'          :  invoice_id.get_purchase_sequence(),
                'specification' :  1,
                'nit'        :  invoice_id.getEmisorNIT(),
                'reazon_social' :  invoice_id.getRazonSocialSupplier(),
                'autorization_code' :  invoice_id.getCuf(),
                'invoice_number'  :  invoice_id.getInvoiceBillNumber(),
                'dui_dim_number' : invoice_id.getDUIDIMNumber(),
                'dui_dim_date' : invoice_id.invoice_date_edi,
                'amount_total'  :  invoice_id.getAmountTotalSupplier(),
                'amount_ice'    :  invoice_id.getAmountIceFromSupplier(),
                'amount_iehd'   :  invoice_id.getAmountIehdFromSupplier(),
                'amount_ipj'    :  invoice_id.getAmountIpjFromSupplier(),
                'amount_rate'   :  invoice_id.getAmountRateFromSupplier(),
                'amount_no_iva' :  invoice_id.getAmountNoIvaFromSupplier(),
                'amount_exempt' :  invoice_id.getAmountExemptFromSupplier(),
                'amount_cero_rate'   :  invoice_id.getAmountZeroRateFromSupplier(),
                'amount_subtotal' : invoice_id.getAmountSubTotalSupplier(),
                'amount_discount' : invoice_id.getAmountDisccountSupplier(),
                'amount_gift_card'    :  invoice_id.getAmountGifCardSuppllier(),
                'amount_base_fiscal_credit' : invoice_id.getAmountOnIvaSupplier(),
                'amount_fiscal_credit' : round(invoice_id.getAmountOnIvaSupplier() * 0.13, 2),
                'purchase_type' : invoice_id.getPurchaseType(),
                'control_code'  : invoice_id.getControlCodeSupplier(),

                'purchase_register_id' : self.id,
            }
            new_l10n_bo_rv_records.append(params)
        if new_l10n_bo_rv_records:
            self.env['l10n.bo.purchase.register.line'].create(new_l10n_bo_rv_records)

    
    def clean_register_olds(self):
        for l10n_bo_standard_rv_id in self.purchase_register_line_ids:
            l10n_bo_standard_rv_id.write({'purchase_register_id': False})

    def action_update(self):
        
        self.clean_register_olds()
        invoice_ids = self.get_invoice_ids()
        _logger.info(f"FACTURAS: {invoice_ids}")
        if invoice_ids:
            new_lines = []
            l10n_bo_rv_list_ids = [ line.invoice_id.id for line in self.purchase_register_line_ids if line.invoice_id ]
            for invoice_id in invoice_ids:
                if invoice_id.id not in l10n_bo_rv_list_ids:
                    new_lines.append(invoice_id)
            
            if new_lines:
                self.create_invoice_records(new_lines)