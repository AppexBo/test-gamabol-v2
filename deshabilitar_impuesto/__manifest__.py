# -*- coding: utf-8 -*-
{
	"name" : "Deshabilitar Impuestos PDV",
	"version" : "17.0.0.0",
	"category" : "Point of Sale",
	"depends" : [
        'base',
        'sale',
        'point_of_sale'
    ],
	"author": "AppexBolivia",
	'summary': 'Este modulo se encarga de cuando una persona registre el dato sin factura anule los impuestos en la linea de la orden, en caso que si se necesite factura se usaran los impuestos que se coloco en el producto.',
	"description": """
		Este modulo se encarga de cuando una persona registre el dato sin factura anule los impuestos en la linea de la orden, en caso que si se necesite factura se usaran los impuestos que se coloco en el producto.
	""",
	"website" : 'https://www.appexbo.com/',
	"data": [
	
    ],
	"installable": True,
    "auto_install": False,
	'license': 'LGPL-3',
}