# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context

import logging
_logger = logging.getLogger(__name__)


class HrBoExpense(models.Model):
    _name ='hr.bo.expense'
    _description='Facturas/Recibos de gastos'

    
    hr_expense_sheet_id = fields.Many2one(
        string='Informe',
        comodel_name='hr.expense.sheet',
    )

    
    state = fields.Selection(
        string='Estado',
        related='hr_expense_sheet_id.state',
        readonly=True,
        store=True
    )
    
    
    
    name = fields.Char(
        string='Descripción',
    )
    
    journal_id = fields.Many2one(
        string='Diario',
        comodel_name='account.journal',
        domain=[
            '|',
            ('bo_purchase_edi', '=', True),
            ('employee_expense_journal', '=', True),
            ('type', '=', 'purchase'),
        ],
        required=True
    )

    
    bo_purchase_edi = fields.Boolean(
        string='Factura de compras',
        related='journal_id.bo_purchase_edi',
        readonly=True,
        store=True
        
    )
    
    
    
    hr_expense_ids = fields.Many2many(
        string='Gastos',
        comodel_name='hr.expense',
        required=True
    )
    
    
    invoice_id = fields.Many2one(
        string='Asiento',
        comodel_name='account.move',
    )
    
    
    partner_id = fields.Many2one(
        string='Proveedor',
        comodel_name='res.partner',
        required=True
    )

    
    invoice_date = fields.Datetime(
        string='Fecha hora',
        required=True
    )

    
    
    
    cuf = fields.Char(
        string='CUF',
        help='Codigo unico de facturacion'
    )
    
    
    invoice_number = fields.Integer(
        string='Nro. Factura',
        help='Numero de factura'
    )
    
    purchase_type = fields.Selection(
        string='Tipo compra',
        selection=[
            ('1', 'Destino a actividades gravadas.'), 
            ('2', 'Destino a actividades no gravadas.'),
            ('3', 'Sujetas a proporcionalidad.'),
            ('4', 'Exportaciones.'),
            ('5', 'Mercado interno/exportaciones')
        ],
        default='1',
        required=True
    )

    dui_dim_number = fields.Char(
        string='Numero DUI/DIM',
        copy=False
    )

    
    control_code = fields.Char(
        string='Codigo control',
        copy=False
    )

    def get_vals_invoice(self):
        self.ensure_one()
        return {
            #'date' : self.invoice_date, #self.hr_expense_sheet_id.accounting_date,
            'move_type' : 'in_invoice',
            'journal_id' : self.journal_id.id,
            'invoice_date_purchase_edi' : self.invoice_date,
            'invoice_date' : self.invoice_date,
            
            'partner_id' : self.partner_id.id,
            'purchase_type' : self.purchase_type,
            'currency_id' : self.hr_expense_sheet_id.currency_id.id,
            'cuf' : self.cuf,
            'invoice_number' : self.invoice_number,
            'purchase_control_code' : self.control_code,
            'dui_dim_number' : self.dui_dim_number
        }
    
    def get_vals_invoice_line(self, move_id):
        line_args = []
        for line in self.hr_expense_ids:
            args = line._prepare_move_lines_vals()
            args['move_id'] = move_id.id
            line_args.append(args)
        
        return line_args


    def create_registries(self):
        self = self.with_context(clean_context(self.env.context))  # remove default_*
        account_vals = self.get_vals_invoice()
        bo_purchase_id : models.Model = self.env['account.move'].create(account_vals)
        bo_purchase_id.write({'date' : self.invoice_date})
        if bo_purchase_id:
                self.env['account.move.line'].create(self.get_vals_invoice_line(bo_purchase_id))
                bo_purchase_id.action_post()
                self.write({'invoice_id' : bo_purchase_id.id})
                

    def validate_fields(self):
        if self.bo_purchase_edi:    
            if self.invoice_number <=0:
                raise UserError('El numero de factura debe ser mayor a cero')
            if not self.cuf:
                raise UserError('El CUF obligatorio para gastos')
