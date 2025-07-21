from odoo import api, models, fields
from odoo.exceptions import UserError

class HrEmployeeReceiptRegister(models.Model):
    _name = 'hr.employee.receipt.register'
    _description='Registro de recibos de empleados'
    
    name = fields.Char(
        string='Nombre',
    )

    
    date_from = fields.Date(
        string='Desde',
    )

    
    date_to = fields.Date(
        string='Hasta',
    )
    
    
    receipt_ids = fields.One2many(
        string='receipt',
        comodel_name='hr.employee.expense.receipt',
        inverse_name='hr_employee_receipt_id',
    )
    
    
    

class HrEmployeeExpenseReceipt(models.Model):
    _name = "hr.employee.expense.receipt"
    _description = "Recibo de gasto de empleados"
    
    
    sequence = fields.Integer(
        string='N°',
        default=0,
        readonly=True
    )
    
    
    specification = fields.Char(
        string='ESPECIFICACIÓN',
        default='1',
        readonly=True 
    )

    
    vat = fields.Char(
        string='NIT PROVEEDOR',
    )
    
    partner_id = fields.Char(
        string='RAZON SOCIAL PROVEEDOR',
    )
    
    authorization_code = fields.Char(
        string='CODIGO DE AUTORIZACION',
        size=100,
        copy=False
    )

    invoice_number = fields.Char(
        string='NUMERO FACTURA',
        copy=False,
        size=20
    )

    
    dui_dim_number = fields.Char(
        string='NÚMERO DUI/DIM',
        copy=False,
        size=15
    )
    
    dui_dim_invoice_date = fields.Date(
        string='FECHA DE FACTURA/DUI/DIM',
        copy=False
    )

    amount_total = fields.Float(
        string='IMPORTE TOTAL COMPRA',
        store=True
    )

    
    amount_ice= fields.Float(
        string='IMPORTE ICE', 
        store=True
    )
    
    
    amount_iehd = fields.Float(
        string='IMPORTE IEHD',
        store=True
    )
    
    
    amount_ipj = fields.Float(
        string='IMPORTE IPJ',
        store=True
    )

    
    rate = fields.Float(
        string='TASAS',
        store=True
    )

    
    amount_no_iva = fields.Float(
        string='OTRO NO SUJETO A CREDITO FISCAL',
        store=True
    )

    
    exempt = fields.Float(
        string='IMPORTES EXENTOS',
        store=True
    )
    
    	
    zero_rate = fields.Float(
        string='IMPORTE COMPRAS GRAVADAS A TASA CERO',
        store=True
    )

    amount_subtotal = fields.Float(
        string='SUBTOTAL',
    )

    
    amount_discount = fields.Float(
        string='DESCUENTOS/BONIFICACIONES /REBAJAS SUJETAS AL IVA',
        store=True
    )

    
    amount_gift_card = fields.Float(
        string='IMPORTE GIFT CARD',
        store=True
    )

    
    amount_tax = fields.Float(
        string='IMPORTE BASE CF',
        compute='_compute_amount_tax', 
        store=True
        
    )
    
    @api.depends('amount_subtotal','amount_discount','amount_gift_card')
    def _compute_amount_tax(self):
        for record in self:
            record.amount_tax = record.amount_subtotal - record.amount_discount - record.amount_gift_card
    
    
    
    amount_fiscal = fields.Float(
        string='CREDITO FISCAL',
        compute='_compute_amount_fiscal', 
        store=True
    )
    
    @api.depends('amount_tax')
    def _compute_amount_fiscal(self):
        for record in self:
            record.amount_fiscal = record.amount_tax * 0.13
    
    
    
    purchase_type = fields.Selection(
        [
            ('1', 'Compras para mercado interno con destino a actividades gravadas'),
            ('2', 'Compras para mercado interno con destino a actividades no gravadas'),
            ('3', 'Compras sujetas a proporcionalidad'),
            ('4', 'Compras para exportaciones'),
            ('5', 'Compras tanto para el mercado interno como para exportaciones'),
        ], 
        string='Tipo de compra', 
        default='1', 
    )

    
    index_purchase_type = fields.Char(
        string='TIPO COMPRA',
        compute='_compute_get_purchase_type' 
    )

    @api.depends('purchase_type')
    def _compute_get_purchase_type(self):
        for record in self:
            record.index_purchase_type = record.purchase_type
    
    control_code = fields.Char(
        string='CÓDIGO DE CONTROL',
        copy=False
    )



    ref = fields.Char(
        string='Rerefencia factura',
    )
    

    
    
    
    account_move_id = fields.Many2one(
        string='Asiento',
        comodel_name='account.move',
    )

    
    hr_employee_receipt_id = fields.Many2one(
        string='Registro de recibo',
        comodel_name='hr.employee.receipt.register',
    )
    
    
    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.company
    )
    