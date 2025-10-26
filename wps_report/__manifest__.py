# -*- coding: utf-8 -*-
{
    'name': 'WPS report for Qatar',
    'author': 'Arcxion',
    "license": "OPL-1",
    'website': 'https://arcxion.com/',
    'support': 'info@arcxion.com',
    'version': '18.0',
    'category': 'Payroll',
    'summary': """WPS report""",
    'description': """WPS report in csv format
    """,
    'depends': ['hr_payroll',
                'hr_holidays'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/wps_report.xml',
        # 'wizard/payroll_transfer_sheet_view.xml',
        # 'views/hr_payslip_views.xml',
        # 'views/res_partner_views.xml',
        # 'views/hr_contract_views.xml',
         'views/hr_employee_views.xml',
        'views/hr_contract_template_views.xml',
        # 'views/hr_leave_views.xml',
        # 'views/payroll_automation_view.xml',
        # 'report/timeoff_report.xml',
        # 'report/timeoff_report_reg.xml',
        # 'report/salary_certificate.xml',
        # 'data/wps_report_data.xml'
    ],
    'images': ['static/description/background.png', ],
    'auto_install': False,
    'installable': True,
    'application': True,
    "price": 95,
    "currency": "EUR"
}
