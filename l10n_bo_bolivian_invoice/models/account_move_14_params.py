from odoo import api, models, fields
from odoo.exceptions import UserError
#import pytz
from decimal import Decimal, ROUND_HALF_UP

from num2words import num2words
import logging
_logger = logging.getLogger(__name__)



class AccountMove14(models.Model):
    _inherit = ['account.move']

    def ice_format(self):
        cabecera = """<cabecera>"""
        cabecera += f"""<nitEmisor>{self.company_id.getNit()}</nitEmisor>"""
        cabecera += f"""<razonSocialEmisor>{self.getCompanyName()}</razonSocialEmisor>"""
        cabecera += f"""<municipio>{self.getMunicipality()}</municipio>"""
        cabecera += f"""<telefono>{self.getPhone()}</telefono>"""
        cabecera += f"""<numeroFactura>{self.invoice_number}</numeroFactura>"""
        cabecera += f"""<cuf>{self.getCuf()}</cuf>"""
        cabecera += f"""<cufd>{self.getCufd()}</cufd>"""
        cabecera += f"""<codigoSucursal>{self.getBranchCode()}</codigoSucursal>"""
        cabecera += f"""<direccion>{self.getAddress()}</direccion>"""
        cabecera += f"""<codigoPuntoVenta>{self.getPosCode()}</codigoPuntoVenta>"""
        cabecera += f"""<fechaEmision>{self.getEmisionDate()}</fechaEmision>"""
        cabecera += f"""<nombreRazonSocial>{self.getNameReazonSocial()}</nombreRazonSocial>"""
        cabecera += f"""<codigoTipoDocumentoIdentidad>{self.partner_id.getIdentificationCode()}</codigoTipoDocumentoIdentidad>"""
        cabecera += f"""<numeroDocumento>{self.getPartnerNit()}</numeroDocumento>"""
        cabecera += f"""<complemento>{self.getPartnerComplement()}</complemento>""" if self.getPartnerComplement() else """<complemento xsi:nil="true"/>"""
        cabecera += f"""<codigoCliente>{self.getPartnerCode()}</codigoCliente>"""
        cabecera += f"""<codigoMetodoPago>{self.getPaymentType()}</codigoMetodoPago>"""
        cabecera += f"""<numeroTarjeta>{self.getCard()}</numeroTarjeta>""" if self.is_card else """<numeroTarjeta xsi:nil="true"/>"""
        cabecera += f"""<montoTotal>{self.amount_total_14(2)}</montoTotal>"""
        cabecera += f"""<montoIceEspecifico>{self.getAmountSpecificIce(2)}</montoIceEspecifico>""" if self.getAmountSpecificIce() > 0 else """<montoIceEspecifico xsi:nil="true"/>"""
        cabecera += f"""<montoIcePorcentual>{self.getAmountPercentageIce(2)}</montoIcePorcentual>""" if self.getAmountPercentageIce() > 0 else """<montoIcePorcentual xsi:nil="true"/>"""
        cabecera += f"""<montoTotalSujetoIva>{self.getAmountOnIva_14(2)}</montoTotalSujetoIva>"""
        cabecera += f"""<codigoMoneda>{self.currency_id.getCode()}</codigoMoneda>"""
        cabecera += f"""<tipoCambio>{self.currency_id.getExchangeRate()}</tipoCambio>"""
        cabecera += f"""<montoTotalMoneda>{self.amountCurrency_14(2)}</montoTotalMoneda>"""
        cabecera += f"""<descuentoAdicional>{self.getAmountDiscount()}</descuentoAdicional>""" if self.getAmountDiscount() != 0 else """<descuentoAdicional xsi:nil="true"/>"""
        cabecera += f"""<codigoExcepcion>{1 if self.force_send else 0}</codigoExcepcion>"""
        cabecera += f"""<cafc>{self.getCafc()}</cafc>""" if self.getCafc() else """<cafc xsi:nil="true"/>"""
        cabecera += f"""<leyenda>{self.getLegend()}</leyenda>"""
        cabecera += f"""<usuario>{self.user_id.name}</usuario>"""
        cabecera += f"""<codigoDocumentoSector>{self.getDocumentSector()}</codigoDocumentoSector>"""
        cabecera += """</cabecera>"""
        
        detalle  = """"""
        for line in self.invoice_line_ids:
            if line.display_type == 'product' and not line.product_id.gif_product:
                detalle  += """<detalle>"""
                detalle += f"""<actividadEconomica>{line.product_id.getAe()}</actividadEconomica>"""
                detalle += f"""<codigoProductoSin>{line.product_id.getServiceCode()}</codigoProductoSin>"""
                detalle += f"""<codigoProducto>{line.product_id.getCode()}</codigoProducto>"""
                detalle += f"""<descripcion>{line.getDescription(to_xml =True)}</descripcion>"""
                detalle += f"""<cantidad>{round(line.quantity,2)}</cantidad>"""
                detalle += f"""<unidadMedida>{line.product_uom_id.getCode()}</unidadMedida>"""
                detalle += f"""<precioUnitario>{line.getPriceUnit()}</precioUnitario>"""
                detalle += f"""<montoDescuento>{line.getAmountDiscount_14(5)}</montoDescuento>""" if line.getAmountDiscount_14() > 0 else """<montoDescuento xsi:nil="true"/>"""
                detalle += f"""<subTotal>{line.getSubtotalCalculateIce(5)}</subTotal>"""
                detalle += f"""<marcaIce>{line.getIceBrand()}</marcaIce>"""
                detalle += f"""<alicuotaIva>{line.getAmountIva_14(5)}</alicuotaIva>"""
                detalle += f"""<precioNetoVentaIce>{line.getAmountIce(5)}</precioNetoVentaIce>"""
                detalle += f"""<alicuotaEspecifica>{line.getSpecificAliquot(5)}</alicuotaEspecifica>"""
                detalle += f"""<alicuotaPorcentual>{line.getPercentageAliquot()}</alicuotaPorcentual>"""
                detalle += f"""<montoIceEspecifico>{line.getSpecificIce(5)}</montoIceEspecifico>"""
                detalle += f"""<montoIcePorcentual>{line.getPercentageIce()}</montoIcePorcentual>"""
                detalle += f"""<cantidadIce>{line.getQuantityIce()}</cantidadIce>""" if line.getQuantityIce() > 0 else """<cantidadIce xsi:nil="true"/>"""
                detalle += """</detalle>"""
            
        return cabecera + detalle
    
    def ice_format_computerized(self):
        purchase_sale = f"""<facturaComputarizadaAlcanzadaIce xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="facturaComputarizadaAlcanzadaIce.xsd">"""
        purchase_sale += self.ice_format()
        purchase_sale += f"""</facturaComputarizadaAlcanzadaIce>"""
        return purchase_sale
    

    def ice_format_electronic(self):

        purchase_sale = f"""<facturaElectronicaAlcanzadaIce xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="/alcanzadaIce/facturaElectronicaAlcanzadaIce.xsd">"""
        purchase_sale += self.ice_format()
        purchase_sale += f"""</facturaElectronicaAlcanzadaIce>"""
        return purchase_sale
    
    def getAmountSpecificIce(self, precision = 2):
        amount_total = 0
        for line in self.invoice_line_ids:
            if line.display_type == 'product' and not line.product_id.gif_product:
                amount_total += line.getSpecificIce()        
        return self.roundingUp(amount_total, precision) if precision else amount_total
    
    def getAmountPercentageIce(self, precision = 2):
        amount_total = 0
        for line in self.invoice_line_ids:
            if line.display_type == 'product' and not line.product_id.gif_product:
                amount_total += line.getPercentageIce()
        return self.roundingUp(amount_total, 2) if precision else amount_total
    
    @api.model
    def roundingUp(self, value, precision):
        return float(Decimal(str(value)).quantize(Decimal('1.' + '0' * precision), rounding=ROUND_HALF_UP))
    
    
    def amount_total_14(self, decimal = None):
        amount = self.amount_subtotal_14(5)
        amount -= self.getAmountDiscount()
        return self.roundingUp(amount, decimal) if decimal else amount
    
    def subTotalBase(self):
        amount = 0
        for line in self.invoice_line_ids:
            amount += line.getSubTotal_14()
        return amount
    
    def amount_subtotal_14(self, decimal = None):
        amount = 0
        for line in self.invoice_line_ids:
            if line.display_type == 'product' and not line.product_id.gif_product:
                amount += line.getSubtotalCalculateIce(5)
        
        return self.roundingUp(amount, decimal) if decimal else amount
    
    def amountCurrency_14(self, decimal = None):
        amount_total = self.amount_total_14() / self.currency_id.getExchangeRate() #self.tax_totals.get('amount_total', 0.00)# / self.currency_id.getExchangeRate()
        return self.roundingUp(amount_total,decimal) if decimal else amount_total
    
    def getAmountOnIva_14(self, decimal = None) -> float:
        #raise UserError(f"{self.amount_total_14(2)} - {self.getAmountSpecificIce(2)} - {self.getAmountPercentageIce(2)}")
        amount = self.amount_total_14(2) - self.getAmountGiftCard()
        amount -= (self.getAmountSpecificIce(2) + self.getAmountPercentageIce(2))
        
        #raise UserError(amount)
        #amount = round(amount - self.getAmountSpecificIce(5) - self.getAmountPercentageIce(), 2)
            #raise UserError(f"ANTES 2 {amount}")
        return self.roundingUp(amount, decimal) if decimal else amount
    

    def getBolivianLiteral14(self):
           
        amount_total = self.amount_total_14(2) #self.getAmountOnIva() if self.document_type_code not in [28, 8, 3] else self.getAmountTotal() # * self.currency_id.getExchangeRate()
        #amount_total += self.getAmountSpecificIce(2) + self.getAmountPercentageIce(2)

        parte_entera = int(amount_total)
        parte_decimal = int( self.roundingUp((amount_total - parte_entera),2) *100)
        parte_decimal = f' {parte_decimal}' if parte_decimal > 10 else f' 0{parte_decimal}'
        return num2words(parte_entera, lang='es') + parte_decimal +'/100'

    
class AccountMoveLine(models.Model):
    _inherit = ['account.move.line']

    
    @api.model
    def roundingUp(self, value, precision):
        return float(Decimal(str(value)).quantize(Decimal('1.' + '0' * precision), rounding=ROUND_HALF_UP))

    def getIceBrand(self):
        return self.product_id.getIceBrand()
    
    def base_14(self, decimal = None):
        base = (self.quantity * self.getPriceUnit() )
        return base
    
    def getAmountDiscount_14(self, decimal = None):
        amount = self.fixed_amount_total_discount
        amount *= (1/self.currency_rate)
        return self.roundingUp(amount, decimal) if decimal else amount
    
    def getSubTotal_14(self, decimal = 2 ):
        if self.display_type == 'product' and not self.product_id.global_discount:
            amount = self.base_14() - self.getAmountDiscount_14()
            _logger.info(f"Monto SUbtotal: {amount}")
            return  self.roundingUp(amount, decimal) if decimal else amount
        return 0
    
    def getSubtotalCalculateIce(self, decimal = None):
        amount = self.getSubTotal_14(5) + self.getSpecificIce(5) + self.getPercentageIce(5)
        amount = self.roundingUp(amount, decimal) if decimal else amount
        return amount
    
    
    def getAmountIva_14(self, decimal = None) -> float:
        base = self.getSubTotal_14(5)
        amount_iva = base * 0.13
        return self.roundingUp(amount_iva, decimal) if decimal else amount_iva
    
    def getAmountIce(self, decimal = None):
        base = self.getSubTotal_14(decimal=5)
        amount = base - self.getAmountIva_14(decimal=5)
        amount = self.roundingUp(amount, decimal) if decimal else amount
        return amount
    
    def getSpecificAliquot(self, decimal = None):
        value = 0
        if self.getIceBrand() == 1:
            value = self.product_id.get_ice_fixed_rate()
        return self.roundingUp(value, decimal) if decimal else value
    
    def getPercentageAliquot(self, decimal = None):
        value = 0
        if self.getIceBrand() == 1:
            value = self.product_id.get_ice_percentage_rate() / 100
        return self.roundingUp(value, decimal) if decimal else value
    
    def getSpecificIce(self, decimal = None)->float:
        amount = 0 
        if self.display_type == 'product' and not self.product_id.global_discount and self.getIceBrand() == 1:
            amount = ((self.getSpecificAliquot() * self.getProductRatio())/ self.getIceRatio() ) * self.quantity
        return self.roundingUp(amount, decimal) if decimal else amount
    
    def getPercentageIce(self, decimal = 5) -> float:
        percentaje_value = 0 
        if self.display_type == 'product' and not self.product_id.global_discount and self.getIceBrand() == 1:
            percentaje_value = self.getPercentageAliquot() * self.getAmountIce()
        return self.roundingUp(percentaje_value ,decimal ) if decimal else percentaje_value
    
    def getIceRatio(self):
        amount = self.product_id.getIceRatio()
        return amount
    
    def getProductRatio(self):
        ratio = self.product_uom_id.ratio
        if ratio <= 0:
            raise UserError(f'No se pudo calcular la cantidad o contenido neto del producto: {self.product_id.name}')
        return ratio
    
    def getQuantityIce(self, decimal = None):
        base = 0
        if self.getIceBrand() == 1:
            base = (self.getProductRatio() / self.getIceRatio()) * self.quantity
        return self.roundingUp(base, decimal) if decimal else base
    
    def apportionment_partial(self):
        total_venta = self.move_id.subTotalBase() # + self.move_id.getAmountLineDiscount()
        total_venta /= self.move_id.currency_id.getExchangeRate()

        base = self.getSubTotal_14() / self.move_id.currency_id.getExchangeRate() #( self.quantity * (self.getPriceUnit() / self.move_id.currency_id.getExchangeRate()) ) - (self.getAmountDiscount() / self.move_id.currency_id.getExchangeRate())
        porcentaje_descuento_prorrateado = ((self.move_id.getAmountDiscount() / self.move_id.currency_id.getExchangeRate() ) * base) / total_venta
        return porcentaje_descuento_prorrateado

    