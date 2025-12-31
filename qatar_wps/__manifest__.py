# -*- coding: utf-8 -*-
{
    'name': 'Qatar WPS Generator',
    'version': '19.0.1.0.0',
    'category': 'Payroll',
    'summary': 'Generate Qatar WPS Salary Information File (SIF)',
    'description': """
        This module allows generating the SIF (Salary Information File) for Qatar Wage Protection System (WPS).
        It supports configuration for multiple employers/payers and standard SIF CSV generation.
    """,
    'author': 'Antigravity',
    'depends': ['hr_payroll', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/wps_config_view.xml',
        'views/hr_employee_view.xml',
        'views/wps_wizard_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}
