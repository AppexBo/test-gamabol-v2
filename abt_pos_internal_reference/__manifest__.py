# -*- coding: utf-8 -*-
{
    'name': 'POS Internal References',
    'author': "AskByte Technolab",
    'summary': """Added internal references for improved tracking.""",
    'description': """
        Internal references are now integrated into the Product Screen, Order Lines, 
        and Receipts, enhancing product management and accuracy throughout transactions.
    """,
    'category': 'Point of Sale',
    'version': '17.0.1.0',
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            ('replace', 'point_of_sale/static/src/app/generic_components/product_card/product_card.xml','abt_pos_internal_reference/static/src/app/generic_components/product_card/product_card.xml'),
            ('replace', 'point_of_sale/static/src/app/screens/product_screen/product_list/product_list.xml','abt_pos_internal_reference/static/src/app/screens/product_screen/product_list/product_list.xml'),
            'abt_pos_internal_reference/static/src/app/store/models.js',
            'abt_pos_internal_reference/static/src/app/generic_components/orderline/orderline.xml'
        ],
    },
    'license': 'LGPL-3',
    'application': True,
    'auto_install': False,
}
