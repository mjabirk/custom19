{
    "name": "fleet productivity",
    "version": "17.03",
    "depends": [
        "fleet",
        "account",
        "woqod_fuel_import",
        "mrp",
        "sale",
        "hr_payroll",
    ],
    "author": "Almisned Technology",
    "category": "Utilities",
    'website': '',
    'price': '100',
    'currency': 'USD',
    'license': 'OPL-1',
    'summary': 'fleet productivity and cost',
    "description": """

Manage
======================================================================
Vehicle productivity analysis report generated using raw data and fleet
Customer Statement Report
BOM Mix Proportions Report
""",
    "data": [
        'views/mrp_bom_views.xml',
        'views/res_partner_views.xml',
        'views/account_payment_views.xml',
        'report/productivity_report_view.xml',
        'report/analysis_report_view.xml',
        'report/customer_statement_report.xml',
        'report/confirmation_of_balance.xml',
        'report/mix_design_report.xml',
        'report/compressive_test_report.xml',
        'report/deferred_details.xml',
        'report/report.xml',
        'report/eos_lp_report.xml',
        'report/report_consumption_analysis_template.xml',
        'wizard/confirmation_balance_wizard.xml',
        'wizard/deferred_details_wizard.xml',
        'wizard/consumption_analysis_view_wiz.xml',
        'wizard/eos_lp_report_wizard.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
