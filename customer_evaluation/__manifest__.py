# -*- coding: utf-8 -*-

{
    'name' : 'Customer Evaluation',
    'version' : '18.2',
    'category': 'Productivity',
    'depends' : [
         'sale_management',
        'account_reports',
        'contacts',
        'analysis_reports'
                ],
    'author': 'Almisned Technology',
    'images': [],
    'price': 99.0,
    'currency': 'EUR',
    'license': 'Other proprietary',
    'summary': 'Customer evaluation based on history and documents',
    'website': 'https://misnedtech.com',
    'description': ''' 
Customer Evaluation
 ''',
    'data' : [
        'views/customer_evaluation_view.xml',
        'security/ir.model.access.csv',
        'security/customer_evaluation.xml',
    ],
    'installable': True,
    'application': False,
}