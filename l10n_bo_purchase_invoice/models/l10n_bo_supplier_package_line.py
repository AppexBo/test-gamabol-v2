# -*- coding:utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError

import pytz
import io
import tarfile
import base64
import gzip
import hashlib
import logging
_logger = logging.getLogger(__name__)



class L10nBoSupplierPackageLine(models.Model):
    _name ="l10n.bo.supplier.package.line"
    _description ="Linea de paquete de proveedor (BO)"

    
    name = fields.Many2one(
        string='Factura',
        comodel_name='account.move',
        domain=[
            ('move_type','=','in_invoice'),
            ('bo_purchase_edi','=',True),
        ]
    )
    
    
    

    
    company_id = fields.Many2one(
        string='Compañia', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.company
    )
    
    

    
    
    supplier_package_id = fields.Many2one(
        string='Paquete.',
        comodel_name='l10n.bo.supplier.package',
    )

    def purchase_soap_service(self, METHOD = None):
        PARAMS = [
                ('name','=',METHOD),
                ('environment_type','=', self.company_id.getL10nBoCodeEnvironment())
        ]
        WSDL_SERVICE = self.env['l10n.bo.purchase.service'].search(PARAMS,limit=1)
        #raise UserError(f"{PARAMS}")
        
        if WSDL_SERVICE:
            #raise UserError(WSDL_SERVICE.getWsdl())
            return getattr(self, f"{METHOD}", False)(WSDL_SERVICE)
        raise UserError(f'Servicio: {METHOD} no encontrado')
    
    bo_purchase_edi_anuled = fields.Boolean(
        string='Factura anulada',
        readonly=True,
    )

    description_anuled = fields.Char(
        string='Desc. Anulacion',
        readonly=True 
    )
    
    state_code_anuled = fields.Integer(
        string='Codigo estado anulacion',
        readonly=True
    )

    error = fields.Text(
        string='Error',
        copy=False
    )
    def anulation_action(self):
        if True:
            if not self.bo_purchase_edi_anuled:
                RESPONSE = self.purchase_soap_service(METHOD='anulacionCompra')
                _logger.info(f"{RESPONSE}")
                if RESPONSE:
                    if type(RESPONSE) == dict:
                        anulation_process = RESPONSE.get('success', False)
                        if anulation_process:
                            DATA : dict = RESPONSE.get('data', False)
                            if DATA:
                                self.name.write(
                                    {
                                        #'edi_state' : DATA.codigoDescripcion,
                                        #'bo_purchase_edi_anuled' : DATA.transaccion,
                                        'bo_purchase_edi_validated' : False
                                    }
                                )
                                self.write(
                                        {
                                            'description_anuled' : DATA.codigoDescripcion,
                                            'state_code_anuled' : DATA.codigoEstado,
                                            'bo_purchase_edi_anuled' : DATA.transaccion,
                                        }
                                    )
                                if DATA.mensajesList:
                                    self.supplier_package_id.set_messages(DATA.mensajesList, self.name)
                                if self.name.state =='posted':
                                    self.name.button_draft()
                                    if self.name.state == 'draft':
                                        self.name.button_cancel()
                        _error = RESPONSE.get('error', False)
                        self.write({'error' : _error})
                        _logger.info(f"ERROR{self.error}")
                        self.supplier_package_id.check_anulation()
                else:
                    self.write({'error' : f"{RESPONSE}"})
            else:
                return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': 'MENSAJE',
                            'message': 'La factura se encuentra anulada/eliminada',
                            'sticky': False,
                        }
                }

    def getCancelationARGS(self):
        return {
            'SolicitudAnulacionCompra' : {
                'codigoAmbiente' : self.company_id.getL10nBoCodeEnvironment(),
                'codigoPuntoVenta': self.supplier_package_id.pos_id.getCode(),
                'codigoSistema': self.company_id.getL10nBoCodeSystem(),
                'codigoSucursal': self.supplier_package_id.branch_office_id.getCode(),
                'cufd': self.supplier_package_id.pos_id.getCufd(True),
                'cuis': self.supplier_package_id.pos_id.getCuis(),
                'nit': self.company_id.getNit(),
                'codAutorizacion' : self.name.getCuf(),
                'nitProveedor' : self.name.getEmisorNIT(),
                'nroDuiDim' : self.name.getDUIDIMNumber(),
                'nroFactura' : self.name.getInvoiceBillNumber()
            }
        }
    def anulacionCompra(self, WSDL_SERVICE):
        OBJECT = self.getCancelationARGS()
        _logger.info(f"PARAMETROS DE ANULACION: {OBJECT}")
        WSDL = WSDL_SERVICE.getWsdl()
        TOKEN = self.company_id.l10n_bo_delegate_token
        WSDL_RESPONSE = WSDL_SERVICE.process_soap_siat(WSDL, TOKEN, OBJECT, 'anulacionCompra')
        return WSDL_RESPONSE