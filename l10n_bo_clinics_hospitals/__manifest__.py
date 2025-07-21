# -*- coding: utf-8 -*-

{
    'name': 'Facturacion clinicas/hopitales.',
    'version': '17.0',
    'author' : 'APPEX BOLIVIA SRL.',
    'summary': 'Facturacion electronica / computarizada',
    'description': """
        Facturacion boliviana electronica / computarizada
    """,
    'depends': [
        'account',
        'l10n_bo_bolivian_invoice'
    ],
    'category': 'Accounting',
    'data': [
        'views/account_move.xml',
        'report/hospital_clinics.xml',
        
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'OPL-1',
    'website': 'https://www.appexbo.com/',
    'maintainer': 'Luis Fernando Hinojosa Flores',
    'contributors': ['Luis Fernando Hinojosa Flores <hinojosafloresluisfernando@gmail.com>']
}
