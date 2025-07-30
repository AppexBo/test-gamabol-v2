{
    'name': 'Linkser by AppexBo',
    'version': '17.0.0.2',
    'description': '',
    'summary': 'Conecta la terminal de pago de linkser',
    
    'author': 'Erick Denis Mercado Oudalova',
    'maintainer': 'AppexBo',
    'company': 'AppexBo',
    'website': 'https://www.appexbo.com/',
    
    
    'category': 'Point of Sale',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mollie_pos_terminal_views.xml',
        'views/mollie_pos_terminal_payments_views.xml',
        'views/res_config_settings_views.xml',
        'views/pos_payment_method_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'mollie_pos_terminal/static/**/*',
        ],
    },
    'license': 'AGPL-3',
}
