# # -*- coding: utf-8 -*-
# # Part of Odoo. See LICENSE file for full copyright and licensing details.
#
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    service_expense_debit_account_id = fields.Many2one(related='company_id.service_expense_debit_account_id', string='Service Expense Debit Account', readonly=False)
    service_expense_credit_account_id = fields.Many2one(related='company_id.service_expense_credit_account_id', string='Service Expense Credit Account', readonly=False)
    service_expense_journal_id = fields.Many2one(related='company_id.service_expense_journal_id', string='Service Expense Journal', readonly=False)
