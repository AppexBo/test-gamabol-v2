{
    'name': 'Personalización de Reporte Boliviano 18',
    'version': '17.0.1.0.0',
    'summary': 'Personaliza el reporte fiscal boliviano de l10n_bo',
    'author': 'APPEX BOLIVIA SRL.',
    'depends': ['base','account','l10n_bo_bolivian_invoice'],
    'data': [
        'views/report_roll_inherit.xml',
        'views/res_company.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
