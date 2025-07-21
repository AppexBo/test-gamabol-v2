{
    'name': 'POS Custom Receipt',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Reemplaza el recibo del Punto de Venta con un diseño personalizado',
    'depends': ['point_of_sale','base'],
    'assets': {
        'point_of_sale._assets_pos': [
            'recibo_punto_venta/static/src/xml/custom_receipt.xml',
        ],
    },
  
    'installable': True,
    'application': False,
}
