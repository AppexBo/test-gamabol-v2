# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.exceptions import UserError
from zeep import Client
import requests
import logging
#from zeep.exceptions import Fault
from zeep import Client, Transport
#from requests.exceptions import ConnectionError as ReqConnectionError, HTTPError, ReadTimeout

from zeep.exceptions import Fault, TransportError, XMLSyntaxError
from requests.exceptions import (
    ConnectionError as ReqConnectionError,
    HTTPError,
    ReadTimeout,
    Timeout,
    RequestException
)

_logger = logging.getLogger(__name__)


class L10nBoOperationService(models.Model):
    _name = 'l10n.bo.operacion.service'
    _description = 'Operaciones de servicio (BO)'


    
    name = fields.Char(
        string='Nombre',
        readonly=True 
    )
    
    
    input = fields.Char(
        string='Entrada',
        readonly=True 
        
    )

    
    output = fields.Char(
        string='Salida',
        readonly=True 
    )
    
    environment_type = fields.Selection(
        string='Tipo entorno',
        selection=[('1', 'Producción'), ('2', 'Pruebas')],
        readonly=True 
    )

    
    modality_type = fields.Selection(
        string='Tipo modalidad',
        selection=[('1', 'Electrónica'), ('2', 'Computarizada')],
        readonly=True, 
        help='Dejar vacio para ambas modalidades.'
    )
    
    
    
    service_type = fields.Selection(
        string='Tipo servicio',
        selection=[
            ('FacturacionSincronizacion', 'Facturacion sincronizacion'),
            ('ServicioFacturacionCompraVenta', 'Facturacion Compra-Venta'), 
            ('FacturacionCodigos', 'Facturacion codigos'), 
            ('FacturacionOperaciones', 'Facturacion operaciones'), 
            ('ServicioFacturacionDocumentoAjuste', 'Nota de credito debito'),
            ('ServicioFacturacionElectronica', 'Facturacion electronica'),
            ('ServicioFacturacionComputarizada', 'Facturacion computarizada'),
            
        ]
    )
    
    
    wsdl_id = fields.Many2one(
        string='Wsdl',
        comodel_name='l10n.bo.wsdl',
        ondelete='restrict',
    )
    
    def getWsdl(self):
        if self.wsdl_id:
            return self.wsdl_id.getWsdl()
        raise UserError(f'El metodo: {self.name} no tiene un servicio wsdl')
    



    def process_soap_siat(self, endpoint, token, params, method):
        headers = {
            "apikey": f"TokenApi {token}"
        }
        session = requests.Session()
        session.headers.update(headers)

        try:
            transport = Transport(session=session)
            client = Client(wsdl=endpoint, transport=transport)
            call_wsdl = getattr(client.service, method)
            soap_response = call_wsdl(**params)
            response = {'success': True, 'data': soap_response}

        except Fault as fault:
            _logger.error("SOAP Fault: %s", fault.message)
            response = {'success': False, 'error': fault.message}

        except TransportError as transport_error:
            _logger.error("SOAP Transport Error: %s", transport_error)
            response = {'success': False, 'error': str(transport_error)}

        except XMLSyntaxError as xml_error:
            _logger.error("SOAP XML Syntax Error: %s", xml_error)
            response = {'success': False, 'error': str(xml_error)}

        except ReqConnectionError as connection_error:
            _logger.error("Connection Error: %s", connection_error)
            response = {'success': False, 'error': str(connection_error)}

        except HTTPError as http_error:
            _logger.error("HTTP Error: %s", http_error)
            response = {'success': False, 'error': str(http_error)}

        except ReadTimeout as timeout_error:
            _logger.error("Read Timeout: %s", timeout_error)
            response = {'success': False, 'error': str(timeout_error)}

        except Timeout as timeout:
            _logger.error("General Timeout: %s", timeout)
            response = {'success': False, 'error': str(timeout)}

        except RequestException as req_error:
            _logger.error("Request Exception: %s", req_error)
            response = {'success': False, 'error': str(req_error)}

        except AttributeError as attr_error:
            _logger.error("Method '%s' not found in SOAP service: %s", method, attr_error)
            response = {'success': False, 'error': f"Method '{method}' not found in SOAP service."}

        except TypeError as type_error:
            _logger.error("Type Error: %s", type_error)
            response = {'success': False, 'error': str(type_error)}

        except Exception as e:
            _logger.exception("Unexpected error:")
            response = {'success': False, 'error': str(e)}
        return response
    