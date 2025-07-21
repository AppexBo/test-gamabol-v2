# -*- coding:utf-8 -*-
{
    'name': 'Módulo Appex, mejora visual FE BO',
    'version': '1.1',
    'author': 'APPEX BOLIVIA SRL.',
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale',
    ],
    'license': 'LGPL-3',
    'summary': (
        'Módulo Appex.\n'
        'Punto de venta .'
    ),
    'description': (
        'Cambios visuales y correcciones minimas.\n\n'
        'Corrección listada: '
        'Caso tarjeta de crédito/débito, 4 primeros y 4 últimos digitos'
        'lorem ipsum.\n\n'
    ),
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'appex_fix_fe_bo/static/src/js/fix_payment_reference_patch.js',
        ],
    },

    'installable': True,
}
