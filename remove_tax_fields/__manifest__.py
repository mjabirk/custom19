{
    'name': 'Remove Tax Fields',
    'version': '1.0',
    'category': 'Sales/Sales',
    'summary': 'Removes tax fields from views, reports, and portal.',
    'description': """
        This module hides tax-related fields from various parts of Odoo:
        - Sales Order form, list, and PDF report
        - Purchase Order form, list, and PDF report
        - Customer Invoice/Vendor Bill form, list, and PDF report
        - Portal views for Sales Orders and Invoices
        It also hides the tax totals section in these documents.
    """,
    'author': 'Arcxion',
    'website': 'https://arcxion.com',
    'depends': [
        'sale_management',
        'purchase',
        'account',
        'portal',
    ],
    'data': [
        'views/sale_views.xml',
        'views/purchase_views.xml',
        'views/account_views.xml',
        'report/sale_report_templates.xml',
        'report/purchase_report_templates.xml',
        'report/account_report_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
