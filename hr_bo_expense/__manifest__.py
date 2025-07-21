# -*- coding: utf-8 -*-

{
    'name': 'Facturación gastos.',
    'version': '17.0',
    'author' : 'APPEX BOLIVIA SRL.',
    'summary': 'Facturacion gastos para empleados',
    'description': """
        Integración de gasto con facturas/recibos para empleados
    """,
    'depends': [
        'contacts',
        'account',
        'hr_expense',
        'l10n_bo_purchase_invoice',
        'l10n_bo_bolivian_invoice',
    ],
    'category': 'Human Resources/Expenses',
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        
        'data/hr_employee_receipt_register.xml',
        'views/hr_expense_sheet.xml',
        'views/hr_bo_expense.xml',
        'views/hr_employee_expense_receipt.xml',
        'views/account_journal.xml',
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'pre_init_hook': '',
    'assets': {},
    'license': 'LGPL-3',
    'website': 'https://www.appexbo.com/',
    'maintainer': 'Luis Fernando Hinojosa Flores',
    'contributors': ['Luis Fernando Hinojosa Flores <hinojosafloresluisfernando@gmail.com>']
}
