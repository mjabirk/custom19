# # -*- coding: utf-8 -*-
# # Part of Odoo. See LICENSE file for full copyright and licensing details.
#
import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools import date_utils
from odoo.tools.misc import format_date


class ResCompany(models.Model):
    _inherit = "res.company"

    service_expense_journal_id = fields.Many2one('account.journal')
    service_expense_debit_account_id = fields.Many2one('account.account', string='Service Expense Debit Account')
    service_expense_credit_account_id = fields.Many2one('account.account', string='Service Expense Credit Account')
