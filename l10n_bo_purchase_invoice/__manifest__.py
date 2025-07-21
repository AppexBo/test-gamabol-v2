# -*- coding: utf-8 -*-

{
    'name': 'Facturación boliviana compras.',
    'version': '17.0',
    'author' : 'APPEX BOLIVIA SRL.',
    'summary': 'Facturacion compras (BO)',
    'description': """
        Registro de compras al SIN
    """,
    'depends': ['account','l10n_bo_bolivian_invoice'],
    'category': 'Accounting',
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/l10n_bo_purchase_wsdl.xml',
        #'data/account_tax_group.xml',
        'data/l10n_bo_purchase_register.xml',
        
        'template/ir_sequence.xml',
        'views/l10n_bo_purchase_service.xml',
        'views/l10n_bo_purchase_wsdl.xml',
        'views/account_journal.xml',
        'views/account_move.xml',
        'views/l10n_bo_supplier_package_line.xml',
        'views/l10n_bo_supplier_package_message.xml',
        'views/l10n_bo_supplier_package.xml',
        'views/l10n_bo_purchase_register_line.xml',
        'views/l10n_bo_purchase_register.xml',
        #'views/res_config_settings.xml',
        'views/account_tax_group.xml',

        'views/menuitem.xml',
        
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'pre_init_hook': '',
    'assets': {},
    'license': 'OPL-1',
    'website': 'https://www.appexbo.com/',
    'maintainer': 'Luis Fernando Hinojosa Flores',
    'contributors': ['Luis Fernando Hinojosa Flores']
}
