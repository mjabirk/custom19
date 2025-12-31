# -*- coding: utf-8 -*-
{
    'name': "HR Offer Letter",
    'summary': """
        Create, manage, and print employee offer letters.""",
    'description': """
        This module allows HR managers to generate professional offer letters for prospective employees. 
        It includes features for managing offer details, salary, benefits, and printing PDF reports.
    """,
    'author': "Arcxion",
    'website': "https://arcxion.com",
    'category': 'Human Resources/Payroll',
    'version': '1.0',
    'depends': ['hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/offer_letter_sequence.xml',
        'report/offer_letter_reports.xml',
        'report/offer_letter_templates.xml',
        'views/offer_letter_views.xml',
        'views/offer_letter_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
