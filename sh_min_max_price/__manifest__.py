# -*- coding: utf-8 -*-
{
    'name': 'Minimum And Maximum Price Of Product',
    'author': 'Almisned Technology',
    'license': 'OPL-1',
    'email': 'info@misnedtech.com ',
    'version': '17.0',
    'category': 'Sales',
    'summary': 'Option to set max and min product price',
    'description': """This module useful to set minimum and maximum selling price for product. Sales person can easily see minimum and maximum sale price so that will useful to make clear action in sales procedure without waiting for senior person.
    product pricelist module, pricelist management app, set product minimum price, select product maximum price, min –max product price odoo
    """,
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_min_max_price.xml',
        'data/sale_order_price_group.xml',
    ],
    'images': ['static/description/background.png', ],
    'auto_install': False,
    'installable': True,
    'application': True,
    "price": 15,
    "currency": "EUR"
}
