# -*- coding:utf-8 -*-
{
    'name': 'Módulo Appex, Descuentos y lealtad FE BO',
    'version': '2.2',
    'author': 'APPEX BOLIVIA SRL.',
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale',
        
    ],
    'license': 'LGPL-3',
    'summary': (
        'Módulo Appex.\n'
        'Punto de venta .'
        'Cambio en Promoción 2x1 múltiple para POS.'
    ),
    'description': (    
        'Intercepta el código de -Descuento y Lealtad- para poder asignar el descuento según el listado de reglas.'
    ),
    'data': [
        #'views/pos_loyalty_rule_views.xml',
        #'views/pos_loyalty_reward_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'appex_promociones_pos/static/src/js/pos_multi_2x1.js',
        ],
    },

    'installable': True,
    'application': False,
}
