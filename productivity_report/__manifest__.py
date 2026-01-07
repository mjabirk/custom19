# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Productivity Report',
    'category': 'Human Resources/Payroll',
    'depends': ['hr_payroll'],
    'email': 'info@misnedtech.com ',
    'website':'',
    'author': 'Almisned Technology',
    'version': '1.0',
    'description': """
Productivity Report
    """,
    'data': [
        'wizard/employee_productivity_wizard_view.xml',
        'wizard/rawdata_consumption_wizard_view.xml',
        'views/productivity_report_report.xml',
        'views/report_employee_productivity_template.xml',
        'views/report_raw_data_consumption.xml',
        'views/delivery_summary_report.xml',
        'security/ir.model.access.csv',
    ],
    'demo': ['data/l10n_in_hr_payroll_demo.xml'],
    'license': 'OEEL-1',
}
