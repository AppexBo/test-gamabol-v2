# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import os

class AccountMove(models.Model):
    _inherit = ['account.move']
    

    def clinics_hospitals_format(self):
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
        cabecera += f"""<numeroDocumento>{self.partner_id.getNit()}</numeroDocumento>"""
        cabecera += f"""<complemento>{self.getPartnerComplement()}</complemento>""" if self.getPartnerComplement() else """<complemento xsi:nil="true"/>"""
        cabecera += f"""<codigoCliente>{self.partner_id.vat}</codigoCliente>"""
        
        cabecera += f"""<modalidadServicio>{self.ref}</modalidadServicio>""" if self.ref else """<modalidadServicio xsi:nil="true"/>"""
        cabecera += f"""<codigoMetodoPago>{self.getPaymentType()}</codigoMetodoPago>"""
        cabecera += f"""<numeroTarjeta>{self.getCard()}</numeroTarjeta>""" if self.is_card else """<numeroTarjeta xsi:nil="true"/>"""
        cabecera += f"""<montoTotal>{self.getAmountTotal()}</montoTotal>"""
        cabecera += f"""<montoTotalSujetoIva>{self.getAmountOnIva()}</montoTotalSujetoIva>"""
        cabecera += f"""<codigoMoneda>{self.currency_id.getCode()}</codigoMoneda>"""
        cabecera += f"""<tipoCambio>{self.currency_id.getExchangeRate()}</tipoCambio>"""
        cabecera += f"""<montoTotalMoneda>{self.amountCurrency()}</montoTotalMoneda>"""
        cabecera += f"""<montoGiftCard>{self.getAmountGiftCard()}</montoGiftCard>""" if self.is_gift_card and self.amount_giftcard > 0 else """<montoGiftCard xsi:nil="true"/>"""
        cabecera += f"""<descuentoAdicional>{self.getAmountDiscount()}</descuentoAdicional>""" if self.amount_discount > 0 else """<descuentoAdicional xsi:nil="true"/>"""
        
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
                detalle += f"""<descripcion>{line.getProductDescription()}</descripcion>"""
                
                detalle += f"""<especialidad>{line.getSpeciality(to_xml = True)}</especialidad>""" if line.getSpeciality() else """<especialidad xsi:nil="true"/>"""
                detalle += f"""<especialidadDetalle>{line.getDescription(to_xml =True)}</especialidadDetalle>""" if line.name else """<especialidad xsi:nil="true"/>"""
                detalle += f"""<nroQuirofanoSalaOperaciones>{line.getRoomNumber()}</nroQuirofanoSalaOperaciones>"""
                detalle += f"""<especialidadMedico>{line.getSpecialityDoctor(to_xml=True)}</especialidadMedico>""" if line.getSpecialityDoctor() else """<especialidadMedico xsi:nil="true"/>"""
                detalle += f"""<nombreApellidoMedico>{line.getDoctorName(to_xml = False)}</nombreApellidoMedico>"""
                detalle += f"""<nitDocumentoMedico>{line.getDoctorNITCODE()}</nitDocumentoMedico>"""
                detalle += f"""<nroMatriculaMedico>{line.getTuition()}</nroMatriculaMedico>""" if line.getTuition() else """<nroMatriculaMedico xsi:nil="true"/>"""                
                detalle += f"""<nroFacturaMedico>{line.getDoctorBillNumber()}</nroFacturaMedico>""" if line.getDoctorBillNumber() > 0 else """<nroFacturaMedico xsi:nil="true"/>"""
                
                detalle += f"""<cantidad>{round(line.quantity,2)}</cantidad>"""
                detalle += f"""<unidadMedida>{line.product_uom_id.getCode()}</unidadMedida>"""
                detalle += f"""<precioUnitario>{line.getPriceUnit()}</precioUnitario>"""
                detalle += f"""<montoDescuento>{line.getAmountDiscount()}</montoDescuento>""" if line.getAmountDiscount() > 0 else """<montoDescuento xsi:nil="true"/>"""
                detalle += f"""<subTotal>{line.getSubTotal()}</subTotal>"""
                detalle += """</detalle>"""
        return cabecera + detalle

    def clinics_hospitals_format_electronic(self):
        _format = f"""<facturaElectronicaHospitalClinica xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"  xsi:noNamespaceSchemaLocation="facturaElectronicaHospitalClinica.xsd">"""
        _format += self.clinics_hospitals_format()
        #_format += """<ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">"""
        #_format += """<!-- Aquí iría la firma digital -->"""
        #_format += """</ds:Signature>"""
        _format += f"""</facturaElectronicaHospitalClinica>"""
        return _format
    
    def clinics_hospitals_format_computerized(self):
        _format = f"""<facturaComputarizadaHospitalClinica xsi:noNamespaceSchemaLocation="facturaComputarizadaHospitalClinica.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">"""
        _format += self.clinics_hospitals_format()
        _format += f"""</facturaComputarizadaHospitalClinica>"""
        return _format
    


    def generate_computerized_format_str(self):
        if self.document_type_id:
            if self.document_type_id.getCode() == 17:
                return self.clinics_hospitals_format_computerized()
        return super(AccountMove, self).generate_computerized_format_str()
        
    def generate_electronic_format_srt(self):
        if self.document_type_id:
            if self.document_type_id.getCode() == 17:
                return self.clinics_hospitals_format_electronic()
        return super(AccountMove, self).generate_electronic_format_srt()
        

    def get_xsd_path(self):
        xsd_name = None
        provider_modality = self.company_id.getL10nBoCodeModality()
        if self.document_type_id:
            if provider_modality == '1':
                if self.document_type_id.getCode() == 17:
                    pass #xsd_name = 'facturaElectronicaHospitalClinica.xsd'   
            elif provider_modality == '2':
                if self.document_type_id.getCode() == 17:
                    xsd_name = 'facturaComputarizadaHospitalClinica.xsd'
        if xsd_name:
            return os.path.join(os.path.dirname(__file__), f'../templates/{xsd_name}')
        return super(AccountMove, self).get_xsd_path()