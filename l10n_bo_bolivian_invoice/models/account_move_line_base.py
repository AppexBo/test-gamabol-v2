# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from xml.sax.saxutils import escape

class AccountMoveLine(models.Model):
    _inherit = ['account.move.line']

    def getQuantity(self, document_type_code):
        if (document_type_code in [28] and self.quantity != 1):
            raise UserError(f"La cantidad del producto servicio: {self.product_id.name} debe ser 1")
        
        if (document_type_code in [8] and self.move_id and self.move_id.pos_id and self.move_id.pos_id.zero_rate_type == 'transportation') and self.quantity != 1:
                raise UserError(f"La cantidad del producto servicio: {self.product_id.name} debe ser 1")
        
        return round(self.quantity, 2)
    

    def getPriceUnit(self):
        if self.move_id.document_type_id.getCode() not in [28, 3, 4]:
            return round( (self.price_unit * (1/self.currency_rate))  , 2)
        return self.price_unit
    
    def getSubTotal(self):
        return round( (self.quantity * self.getPriceUnit() ) - self.getAmountDiscount() , 2)
    
    def getSpeciality(self):
        if self.product_id.categ_id:
            return self.product_id.categ_id.name
        return False
    
    

    

    def getDescription(self, to_xml=False):
        stringCode = f"[{self.product_id.getCode()}]"
        description = self.name.replace(stringCode, '').strip()
        description = description.replace('\n', ' ').replace('\r', '')
        if to_xml:
            return escape(description)
        return description
            

    
    
    
    #def getIceBrand(self):
    #    return self.product_id.getIceBrand()
    
    def getAmountIva(self, decimal = 2) -> float:
        #base = self.quantity * self.getPriceUnit()
        base = self.getSubTotal()
        #if self.move_id.document_type_id.getCode() in [14]:
        #    base -= self.getCalculateIce()
        amount_iva = base * 0.13
        return round(amount_iva, decimal)
    
    #def getAmountIce(self):
    #    base = self.getSubTotal()
    #    return round(base - self.getAmountIva(), 5)
    
    #def getSpecificAliquot(self):
    #    value = 0
    #    if self.getIceBrand() == 1:
    #        value = self.product_id.get_ice_fixed_rate()
    #    return round(value, 2)
    
    #def getPercentageAliquot(self):
    #    value = 0
    #    if self.getIceBrand() == 1:
    #        value = self.product_id.get_ice_percentage_rate() / 100
    #    return round(value, 2)
    
    # def getIceRatio(self):
    #     return self.product_id.getIceRatio()
    
    # def getProductRatio(self):
    #     ratio = self.product_uom_id.ratio
    #     if ratio <= 0:
    #         raise UserError(f'No se pudo calcular la cantidad o contenido neto del producto: {self.product_id.name}')
    #     return ratio
    
    #def getSpecificIce(self)->float:
        #amount = (self.getSpecificAliquot() * self.getProductRatio()) / 1000 # /1000ml
    #    amount = 0 
    #    if self.getIceBrand() == 1:
    #        amount = ((self.getSpecificAliquot() * self.getProductRatio())/ self.getIceRatio() ) * self.quantity
            #amount = self.roundingUpDecimal(amount)
    #    return round(amount ,5)
    
    #def getPercentageIce(self) -> float:
    #    percentaje_value = 0 
    #    if self.getIceBrand() == 1:
    #        percentaje_value = self.getPercentageAliquot() * self.getAmountIce()
    #    return round(percentaje_value ,5)
    

    # def getQuantityIce(self):
    #     base = 0
    #     if self.getIceBrand() == 1:
    #         base = (self.getProductRatio() / self.getIceRatio()) * self.quantity
    #     return round(base,2)
    
    #def getSubtotalCalculateIce(self):
    #    return round(self.getSubTotal() + self.getSpecificIce() + self.getPercentageIce(), 5)
    

    # ---------------------------
    
    