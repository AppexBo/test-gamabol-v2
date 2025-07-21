# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class LineDiscount(models.TransientModel):
    _name = 'line.discount'
    _description ="Descuento por linea"

    
    
    
    name = fields.Many2one(
        string='Linea de factura',
        comodel_name='account.move.line',
    )

    
    type = fields.Selection(
        string='Tipo',
        selection=[('amount', 'Monto'), ('percentage', 'Porcetaje')],
        default='amount',
        required=True
    )

    
    amount = fields.Float(
        string='Monto',
    )

    
    percentage = fields.Float(
        string='Porcentaje',
    )
    
    def action_done(self):
        self.discounting()
        return {'type': 'ir.actions.act_window_close'}
    
    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
    
    @api.onchange('percentage')
    @api.constrains('percentage')
    def _check_percentage(self):
        for record in self:
            if record.type == 'percentage':
                amount = (record.name.quantity * record.name.price_unit)  * (record.percentage / 100)
                self.write({'amount': amount})
    

    def discounting(self):
        if self.name:
            if self.type == 'amount':
                if self.amount < (self.name.quantity * self.name.getPriceUnit() ):
                    self.name.write({'proportional_discount' : self.amount / self.name.quantity, 'amount_discount' : self.amount, 'fixed_amount_total_discount': self.amount, 'discount' : 0})
                else:
                    raise UserError('El descuento no puede superar el subtotal')
            else:
                if self.percentage < 100:
                    self.name.write({'proportional_discount' : 0, 'amount_discount' : 0, 'discount' : self.percentage, 'fixed_amount_total_discount': self.amount})
                else:
                    raise UserError('El descuento no puede ser mayor o igual al 100%')
            #self.name._amount_discount()
    


class AccountMoveLineBase(models.Model):
    _inherit = ['account.move.line']
    

    amount_discount = fields.Float(
        string='Desc. Fijo',
    )

    fixed_amount_total_discount = fields.Float(
        string='fixed amount total discount',
        readonly=True
    )

    proportional_discount = fields.Float(
        string='Descuento proporcional',
    )
    prorated_line_discount = fields.Float(
        string='Descuento total prorateado',
        help='Acumula el descuento por linea correspondiente + el descuento global prorateado',
        copy=False,
        readonly=True
    )
    
    fixed_discount = fields.Boolean(
        string='¿Descuento fijo?',
        readonly=True
    )

    percent_discount = fields.Boolean(
        string='¿Descuento porcentaje?',
        copy=False,
        readonly=True
    )

    

    
    
    
    
    #@api.onchange('amount_discount')
    #@api.constrains('amount_discount')
    # def _amount_discount(self):
    #     for record in self:
    #         if record.quantity > 0 and record.price_unit > 0:
    #             if record.getAmountDiscount() < (record.getSubTotal() + record.getAmountDiscount()):
    #                 monto = record.quantity * record.price_unit
    #                 disc = (100 * (monto-record.amount_discount))/monto

    #                 #monto_formateado = "{:.10f}".format(monto)  # Aquí se especifica la precicion de decimales
                
    #                 record.write({'fixed_discount' : record.amount_discount>0})
    #                 record.write({'discount' : ( disc - 100)*-1})
    #             else:
    #                 raise UserError('El descuento no puede superar el subtotal')
    #         else:
    #             raise UserError('La cantidad y el precio deben ser mayor a cero')
                
    

    # def getAmountDiscount(self): # METHOD 1
    #     amount = self.amount_discount
    #     if self.move_id.document_type_id.getCode() not in [28]: # /|\ ADD MORE DOCUMENTS TO RATE CONVERT  ...
    #         amount *= (1/self.currency_rate)
    #     return round(amount,2 )

    def getAmountDiscount(self, decimal = None): # METHOD 2
        amount = self.fixed_amount_total_discount
        if self.move_id.document_type_id.getCode() not in [3]: # /|\ ADD MORE DOCUMENTS TO RATE CONVERT  ...
            amount *= (1/self.currency_rate)
        return round(amount,2 )
    

    
    #@api.onchange('discount')
    #@api.constrains('discount')
    # def _discount(self):
    #     for record in self:
    #         if not record.fixed_discount and record.move_id and record.move_id.create_date:
    #             record.write({'percent_discount' : record.discount > 0})
    #             record.write({'amount_discount' : ((record.quantity * record.price_unit) * (record.discount/100) ) if record.discount>0 else 0})

        
    def line_discount_wizard(self):
        if self.display_type == 'product' and not self.product_id.gif_product:
            return {
                'name': 'Descuento por linea',
                'type': 'ir.actions.act_window',
                'res_model': 'line.discount',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_name': self.id
                }
            }
        

    
    
    
    
    
    def ap(self):
        porcentaje_descuento_prorrateado = self.apportionment_partial()
        apportionment = porcentaje_descuento_prorrateado + (self.getAmountDiscount() / self.move_id.currency_id.getExchangeRate())
                
        return apportionment 

    def apportionment(self): # METHOD 2
        if self.getSubTotal() > 0:
            if self.move_id.document_type_id.getCode() in [14]:
                #total_venta = self.getAmountSubTotalWithOutICE()# + self.move_id.getAmountLineDiscount()

                #total_venta /= self.move_id.currency_id.getExchangeRate()
                #_logger.info(f'Total venta: {total_venta}')

                #base = self.getSubTotal() / self.move_id.currency_id.getExchangeRate() #( self.quantity * (self.getPriceUnit() / self.move_id.currency_id.getExchangeRate()) ) - (self.getAmountDiscount() / self.move_id.currency_id.getExchangeRate())
                #raise UserError(base)
            
                #base += self.getSpecificIce() + self.getPercentageIce()
                
                
                #porcentaje_descuento_prorrateado = ((self.move_id.getAmountDiscount() / self.move_id.currency_id.getExchangeRate() ) * base) / total_venta
                #porcentaje_descuento_prorrateado = self.apportionment_partial()
                apportionment = self.ap() #porcentaje_descuento_prorrateado + (self.getAmountDiscount() / self.move_id.currency_id.getExchangeRate())
                self.write(
                    {
                        'prorated_line_discount' : round(apportionment, 2)
                    }
                )

            else:
                total_venta = (self.move_id.amountCurrency() * self.move_id.currency_id.getExchangeRate()) + self.move_id.getAmountDiscount() + self.move_id.getAmountLineDiscount()
                porcentaje_descuento_prorrateado = self.move_id.getAmountDiscount() / total_venta
                apportionment = round(porcentaje_descuento_prorrateado * (self.getSubTotal() + self.getAmountDiscount() ), 2)
                apportionment += self.getAmountDiscount()
                self.write(
                    {
                        'prorated_line_discount' : round(apportionment, 2)
                    }
                )

    def _get_discount_from_fixed_discount(self):
        self.ensure_one()
        currency = self.currency_id or self.company_id.currency_id
        if float_is_zero(self.proportional_discount, precision_rounding=currency.rounding):
            return 0.0
        return (self.proportional_discount / self.price_unit) * 100

    # def apportionment(self): # METHOD 1
    #     if self.getSubTotal() > 0:
    #         total_venta = (self.move_id.amountCurrency() * self.move_id.currency_id.getExchangeRate()) + self.move_id.getAmountDiscount() + self.move_id.getAmountLineDiscount()
    #         porcentaje_descuento_prorrateado = self.move_id.getAmountDiscount() / total_venta
    #         apportionment = round(porcentaje_descuento_prorrateado * (self.getSubTotal() + self.getAmountDiscount() ), 2)
    #         apportionment += self.getAmountDiscount()
    #         self.write(
    #             {
    #                 'prorated_line_discount' : round(apportionment, 2)
    #             }
    #         )


    """
        1 validar asientos masivamente
        2 Crear producto giftcard
        3 Agregar codigo de recepcion y de validacion,  estado en el envio de paquetes masivos
    """

    
    

    




class AccountMove(models.Model):
    _inherit = ['account.move']
    

    def getAmountLineDiscount(sefl):
        amount = 0
        for line in sefl.invoice_line_ids:
            if not line.product_id.global_discount:
                amount += line.getAmountDiscount()
        return amount