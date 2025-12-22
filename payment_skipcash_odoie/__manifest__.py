# -*- coding: utf-8 -*-
# Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details
{
    'name': 'SkipCash Payment Gateway',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 1,
    'summary': 'Odoo SkipCash Payment Gateway',
    'description': 'Odoo SkipCash Payment Gateway',
    'author': 'Odoie',
    'website': 'https://www.odoie.com/',
    'depends': ['base','payment'],
    'data': [
        'views/payment_skipcash_templates.xml',
        'views/payment_provider_views.xml',
        'data/payment_provider_data.xml',
    ],
    'images': [
        'static/description/banner.png'
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
    'price': 150,
    'currency': 'USD',
    'external_dependencies': {
        "python": ["skipcash"],
    },
}
