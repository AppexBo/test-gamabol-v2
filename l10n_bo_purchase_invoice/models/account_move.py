# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
import os
import base64
from odoo.exceptions import ValidationError
from lxml import objectify
from lxml import etree

import pytz
import logging
_logger = logging.getLogger(__name__)



class AccountMove(models.Model):
    _inherit = ['account.move']
    
    # FIELDS
    bo_purchase_edi = fields.Boolean(
        string='Factura compra (BO)',
        related='journal_id.bo_purchase_edi',
        readonly=True,
        store=True
    )

    
    invoice_date_purchase_edi = fields.Datetime(
        string='Fecha hora',
        default=fields.Datetime.now,
        help='Fecha hora factura compra'        
    )

    
    @api.onchange('invoice_date_purchase_edi')
    @api.constrains('invoice_date_purchase_edi')
    def _check_invoice_date_purchase_edi(self):
        for record in self:
            if record.move_type == 'in_invoice':
                record.write({'invoice_date' : record.invoice_date_purchase_edi})
    
    
    
    def getEmisionDateProviderPurchase(self):
        fecha_hora_bolivia = self.invoice_date_purchase_edi.astimezone(pytz.timezone('America/La_Paz'))
        #_datetime = fecha_hora_bolivia.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] 
        #raise UserError(f"{}")
        return  fecha_hora_bolivia.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] 
    
    bo_purchase_edi_validated = fields.Boolean(
        string='Factura compra validada',
        copy=False
    )

    purchase_type = fields.Selection(
        string='Tipo compra',
        selection=[
            ('1', '(1) Compras para mercado interno con destino a actividades gravadas.'), 
            ('2', '(2) Compras para mercado interno con destino a actividades no gravadas.'),
            ('3', '(3) Compras sujetas a proporcionalidad.'),
            ('4', '(4) Compras para exportaciones.'),
            ('5', '(5) Compras tanto para el mercado interno como para exportaciones')
        ],
        default='1',
        required=True
    )

    edi_purchase_str = fields.Text(
        string='Formato compra EDI',
        copy=False,
        readonly=True
    )

    dui_dim_number = fields.Char(
        string='Numero DUI/DIM',
        copy=False
    )

    
    purchase_control_code = fields.Char(
        string='Codigo control',
        copy=False
    )
    

    

    

    def next_purchase_sequence(self):
        for record in self:
            if record.bo_purchase_edi:
                record.journal_id.next_purchase_sequence()
        
    purchase_sequence = fields.Integer(
        string='Secuencia compra',
        copy=False
    )
    
    def get_purchase_sequence(self):
        for record in self:
            if record.bo_purchase_edi and record.purchase_sequence == 0:
                record.write({'purchase_sequence' : record.journal_id.get_purchase_sequence()})
            return record.purchase_sequence
        
    
    
    def getAmountTotalSupplier(self, decimal = None) -> float :
        amount_total = 0
        for line in self.invoice_line_ids:
            if line.display_type == 'product' and not line.product_id.global_discount:
                amount_total += line.quantity * line.price_unit
        #raise UserError(self.getAmountDisccountSupplier())
        amount_total += self.getAmountDisccountSupplier()
        if decimal:
            return self.roundingUp(amount_total, decimal)
        return amount_total
    
    def getAmountSubTotalSupplier(self, decimal = None):
        amount = self.getAmountTotalSupplier() - self.getAmountIceFromSupplier() - self.getAmountIehdFromSupplier() - self.getAmountIpjFromSupplier() - self.getAmountRateFromSupplier() - self.getAmountNoIvaFromSupplier() - self.getAmountExemptFromSupplier() - self.getAmountZeroRateFromSupplier()
        return self.roundingUp(amount, decimal) if decimal else amount

    def getAmountDisccountSupplier(self, decimal = None):
        amount = self.getAmountDiscount() + self.getAmountLineDiscount()
        return self.roundingUp(amount, decimal) if decimal else amount
    
    def getAmountGifCardSuppllier(self):
        return self.getAmountGiftCard()
    
    def getControlCodeSupplier(self):
        return self.purchase_control_code if self.purchase_control_code else '0'
    # -- TAXS --

    def get_purchase_edi_group(self, group_id):
        account_tax_group = self.sudo().env['account.tax.group'].search([('id','=',group_id)], limit=1)
        #raise UserError(account_tax_group)
        return account_tax_group.purchase_tax_group_type if account_tax_group and account_tax_group.purchase_tax_group_type else False

    def get_purchase_group_amount(self, group_name):
        _logger.info(f"Buscando impuesto del grupo: {group_name}")
        amount = 0
        if self.tax_totals:
            groups = self.tax_totals.get('groups_by_subtotal', [])
            #raise UserError(f"{groups}")
            _logger.info(f"{groups}")
            if groups:
                base_list = groups.get('Subtotal', [])
                _logger.info(f"{base_list}")
                #raise UserError(f"{base_list}")
                if base_list:
                    for base in base_list:
                        account_tax_group = self.get_purchase_edi_group(base.get('tax_group_id'))
                        #raise UserError(account_tax_group)
                        if account_tax_group:
                            #base_name = base.get('tax_group_name', '')
                            #_logger.info(f"{base_name}")
                            #raise UserError(account_tax_group == group_name)
                            if account_tax_group == group_name:
                                _logger.info('Encontrado')
                                #raise UserError(f"{base}")
                                base_amount = base.get('tax_group_amount', False)
                                if base_amount:
                                    amount += base_amount
                                    #break
        return amount
    
    def getAmountIceFromSupplier(self, decimal = None):
        #tax_group = self.env.ref('l10n_bo_purchase_invoice.tax_ice_purchase_group', False)
        #raise UserError(self.get_purchase_group_amount('ice'))
        return self.roundingUp(self.get_purchase_group_amount('ice'), decimal) if decimal else self.get_purchase_group_amount('ice') # if tax_group else 0
    
    def getAmountIehdFromSupplier(self, decimal = None):
        #tax_group = self.env.ref('l10n_bo_purchase_invoice.tax_iehd_purchase_group', False)
        return self.roundingUp(self.get_purchase_group_amount('iehd'), decimal) if decimal else self.get_purchase_group_amount('iehd') # if tax_group else 0
        #return round(self.get_purchase_group_amount('iehd'), 2) #if tax_group else 0
    
    def getAmountIpjFromSupplier(self, decimal = None):
        #tax_group = self.env.ref('l10n_bo_purchase_invoice.tax_ipj_purchase_group', False)
        return self.roundingUp(self.get_purchase_group_amount('ipj'), decimal) if decimal else self.get_purchase_group_amount('ipj') # if tax_group else 0
        #return round(self.get_purchase_group_amount('ipj'), 2) #if tax_group else 0
    
    def getAmountRateFromSupplier(self, decimal = None):
        #tax_group = self.env.ref('l10n_bo_purchase_invoice.tax_rate_purchase_group', False)
        return self.roundingUp(self.get_purchase_group_amount('rate'), decimal) if decimal else self.get_purchase_group_amount('rate') # if tax_group else 0
        #return round(self.get_purchase_group_amount('rate'), 2) #if tax_group else 0
    
    def getAmountNoIvaFromSupplier(self, decimal = None):
        #tax_group = self.env.ref('l10n_bo_purchase_invoice.tax_no_iva_purchase_group', False)
        return self.roundingUp(self.get_purchase_group_amount('no_iva'), decimal) if decimal else self.get_purchase_group_amount('no_iva') # if tax_group else 0
        #return round(self.get_purchase_group_amount('no_iva'), 2) #if tax_group else 0
    
    def getAmountExemptFromSupplier(self, decimal = None):
        #tax_group = self.env.ref('l10n_bo_purchase_invoice.tax_exempt_purchase_group', False)
        return self.roundingUp(self.get_purchase_group_amount('exempt'), decimal) if decimal else self.get_purchase_group_amount('exempt') # if tax_group else 0
        #return round(self.get_purchase_group_amount('exempt'), 2) #if tax_group else 0
    
    def getAmountZeroRateFromSupplier(self, decimal = None):
        #tax_group = self.env.ref('l10n_bo_purchase_invoice.tax_zero_rate_purchase_group', False)
        return self.roundingUp(self.get_purchase_group_amount('cero_rate'), decimal) if decimal else self.get_purchase_group_amount('cero_rate') # if tax_group else 0
        #return round(self.get_purchase_group_amount('cero_rate'), 2) #if tax_group else 0
    
    def getAmountOnIvaSupplier(self, decimal = None):
        amount = self.getAmountSubTotalSupplier() - self.getAmountDisccountSupplier() - self.getAmountGifCardSuppllier()
        if decimal:
            return self.roundingUp(amount, decimal)
        return amount

    def edi_purchase_format(self):
        cabecera = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>"""
        cabecera += """<registroCompra>"""
        cabecera += f"""<nro>{self.get_purchase_sequence()}</nro>"""
        cabecera += f"""<nitEmisor>{self.getEmisorNIT()}</nitEmisor>"""
        cabecera += f"""<razonSocialEmisor>{self.getRazonSocialSupplier()}</razonSocialEmisor>"""
        cabecera += f"""<codigoAutorizacion>{self.getCuf()}</codigoAutorizacion>"""
        cabecera += f"""<numeroFactura>{self.getInvoiceBillNumber()}</numeroFactura>"""
        cabecera += f"""<numeroDuiDim>{self.getDUIDIMNumber()}</numeroDuiDim>"""
        cabecera += f"""<fechaEmision>{self.getEmisionDateProviderPurchase()}</fechaEmision>"""
        cabecera += f"""<montoTotalCompra>{self.getAmountTotalSupplier(2)}</montoTotalCompra>"""
        cabecera += f"""<importeIce>{self.getAmountIceFromSupplier(2)}</importeIce>"""
        cabecera += f"""<importeIehd>{self.getAmountIehdFromSupplier(2)}</importeIehd>"""
        cabecera += f"""<importeIpj>{self.getAmountIpjFromSupplier(2)}</importeIpj>"""
        cabecera += f"""<tasas>{self.getAmountRateFromSupplier(2)}</tasas>"""
        cabecera += f"""<otroNoSujetoCredito>{self.getAmountNoIvaFromSupplier(2)}</otroNoSujetoCredito>"""
        cabecera += f"""<importesExentos>{self.getAmountExemptFromSupplier(2)}</importesExentos>"""
        cabecera += f"""<importeTasaCero>{self.getAmountZeroRateFromSupplier(2)}</importeTasaCero>"""
        cabecera += f"""<subTotal>{self.getAmountSubTotalSupplier(2)}</subTotal>"""
        cabecera += f"""<descuento>{self.getAmountDisccountSupplier()}</descuento>"""
        cabecera += f"""<montoGiftCard>{self.getAmountGifCardSuppllier()}</montoGiftCard>"""
        cabecera += f"""<montoTotalSujetoIva>{self.getAmountOnIvaSupplier(2)}</montoTotalSujetoIva>"""
        cabecera += f"""<creditoFiscal>{round(self.getAmountOnIvaSupplier(2) * 0.13, 2)}</creditoFiscal>"""
        cabecera += f"""<tipoCompra>{self.getPurchaseType()}</tipoCompra>"""
        cabecera += f"""<codigoControl>{self.getControlCodeSupplier()}</codigoControl>"""
        cabecera += """</registroCompra>"""
        return cabecera
    
    def getEmisorNIT(self):
        if self.partner_id:
            if self.partner_id.vat:
                return self.partner_id.vat
            raise UserError(f"El proveedor: {self.partner_id.name} no tiene NIT")
        raise UserError('No tiene un proveedor establesido en la factura')
    
    def getInvoiceBillNumber(self):
        if self.invoice_number > 0:
            return self.invoice_number
        raise UserError('El Nro. Factura debe ser mayor a cero 0')

    def getRazonSocialSupplier(self):
        nombreRazonSocial : str = self.partner_id.name
        nombreRazonSocial = nombreRazonSocial.replace('&','&amp;')
        return nombreRazonSocial
    
    def getDUIDIMNumber(self):
        if self.dui_dim_number:
            return self.dui_dim_number
        return 0
    
    
    
    def getPurchaseType(self):
        if self.bo_purchase_edi:
            if self.purchase_type:
                _logger.info(self.purchase_type)
                return self.purchase_type
            raise UserError('No tiene un tipo de compra establecido.')
        
    
    

    def generate_edi_purchase_xml(self, _ir = False):
        if self.edi_purchase_str:
            edi_tree_signed = self.edi_purchase_str.encode('utf-8')
            _name_file = f'{self.name} RECEPCION (BO) - XML'

            attacht_id = self.env['ir.attachment'].search(
                [
                    ('res_model', '=', self._name),
                    ('res_id', '=', self.id),
                    ('name', '=', _name_file)
                ]
                ,limit=1
            )
            
            if not attacht_id:
                if not _ir:
                    attacht_id = self.env['ir.attachment'].create({
                        'res_model': self._name,
                        'res_id': self.id,
                        'type': 'binary',
                        'name': _name_file,
                        'datas': base64.b64encode(edi_tree_signed),
                        'mimetype': 'application/xml',
                        'tax_document' : True
                    })
                else:
                    raise UserError(f'No se encontro XML de factura de proveedores, {self.name}')
            else:
                if _ir:
                    return attacht_id
                attacht_id.write({'datas': base64.b64encode(edi_tree_signed), 'mimetype': 'application/xml',})
        else:
            _logger.info(f"La factura: {self.name} no genero un XML")
            
    def generate_confirmation_edi_purchase_xml(self, _edi_str = False, _ir = False):
        if self.edi_purchase_str:
            if _edi_str:
                edi_tree_signed = _edi_str.encode('utf-8')
            _name_file = f'{self.name} CONFIRMACION (BO) - XML'

            attacht_id = self.env['ir.attachment'].search(
                [
                    ('res_model', '=', self._name),
                    ('res_id', '=', self.id),
                    ('name', '=', _name_file)
                ]
                ,limit=1
            )
            
            if not attacht_id:
                if not _ir or _edi_str:
                    attacht_id = self.env['ir.attachment'].create({
                        'res_model': self._name,
                        'res_id': self.id,
                        'type': 'binary',
                        'name': _name_file,
                        'datas': base64.b64encode(edi_tree_signed),
                        'mimetype': 'application/xml',
                        'tax_document' : True
                    })
                else:
                    raise UserError(f'No se encontro XML de factura de proveedores, {self.name}')
            else:
                if _ir:
                    return attacht_id
                if _edi_str:
                    attacht_id.write({'datas': base64.b64encode(edi_tree_signed), 'mimetype': 'application/xml',})
        else:
            _logger.info(f"La factura: {self.name} no genero un XML")
            
        
        
    def generate_edi_purchase_str(self):
        self.write({'edi_purchase_str' : self.edi_purchase_format()})
        _logger.info("Formato EDI Purchase")
        _logger.info(f"{self.edi_purchase_str}")
    
    def _action_purchase_edi(self):
        if self.move_type == 'in_invoice':
            self.generate_edi_purchase_str()
            self.validate_edi_purchase_xml()
            self.generate_edi_purchase_xml()

    def _post_purchase_edi(self):
        if self.move_type == 'in_invoice':
            self.next_purchase_sequence()

    def _post(self,soft=True):
        res = super(AccountMove, self)._post(soft=soft)
        for record in res:
            if record.bo_purchase_edi:
                record._action_purchase_edi()
                record._post_purchase_edi()
        
        return res

    
    @api.constrains('invoice_date_edi')
    def _check_purchase_invoice_date_edi(self):
        for record in self:
            if record.bo_purchase_edi and record.move_type in ['in_invoice']:
                fechaHora = record.invoice_date_edi.astimezone(pytz.timezone('America/La_Paz'))
                record.write({'invoice_date' : fechaHora, 'date': fechaHora})


    def validate_edi_purchase_xml(self):
        for record in self:
            if record.edi_purchase_str:
                # Ruta absoluta al archivo XSD
                xsd_path = os.path.join(os.path.dirname(__file__), '../data/registroCompra.xsd')
                self._validate_xml(record.edi_purchase_str, xsd_path)


    def _validate_xml(self, xml_str, xsd_path):
        try:
            with open(xsd_path, 'rb') as xsd_file:
                xmlschema_doc = etree.parse(xsd_file)
                xmlschema = etree.XMLSchema(xmlschema_doc)
                
            parser = etree.XMLParser(recover=True)
            xml_doc = etree.fromstring(xml_str.encode('utf-8'), parser)

            if not xmlschema.validate(xml_doc):
                # Obtener los errores de validación
                log = xmlschema.error_log
                error_details = "\n".join([f"Linea {error.line}: {error.message}" for error in log])
                raise ValidationError(f"El XML no es válido según el esquema XSD proporcionado.\nErrores:\n{error_details}")
        except (etree.XMLSyntaxError, etree.XMLSchemaParseError) as e:
            raise ValidationError(f"Error al analizar el XML o el esquema XSD: {str(e)}")
        except IOError as e:
            raise ValidationError(f"No se pudo leer el archivo XSD: {str(e)}")

    def errorMessague(self):
        for record in self:
            if record.bo_purchase_edi_validated:
                raise UserError('Accion no valida para documentos fiscales de compras, esta factura esta procesada por el envio de paquetes (BO) al SIN.')
        
    def button_draft(self):
        self.errorMessague()
        res = super(AccountMove, self).button_draft()
        return res
    
    def confirmation_edi_purchase_format(self):
        cabecera = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>"""
        cabecera += """<confirmacionCompra>"""
        cabecera += f"""<nro>{self.get_purchase_sequence()}</nro>"""
        cabecera += f"""<nitEmisor>{self.getEmisorNIT()}</nitEmisor>"""
        cabecera += f"""<codigoAutorizacion>{self.getCuf()}</codigoAutorizacion>"""
        cabecera += f"""<numeroFactura>{self.getInvoiceBillNumber()}</numeroFactura>"""
        cabecera += f"""<tipoCompra>{self.getPurchaseType()}</tipoCompra>"""
        cabecera += """</confirmacionCompra>"""
        return cabecera
    
    def validate_confirmation_edi_purchase_xml(self):
        for record in self:
            xsd_path = os.path.join(os.path.dirname(__file__), '../data/confirmacionCompra.xsd')
            record._validate_xml(record.confirmation_edi_purchase_format(), xsd_path)
            record.generate_confirmation_edi_purchase_xml(_edi_str = record.confirmation_edi_purchase_format())