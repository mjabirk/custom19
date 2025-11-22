# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _


class ConfirmationBalanceWizard(models.TransientModel):
    _name = 'confirmation.balance.wizard'
    _description = 'Confirmation Of Balance'

    partner_id = fields.Many2one('res.partner', string='Partner',help='Keep blank to generate report for all customers')
    date = fields.Date(string='Date', required=True, default=fields.Date.today())
    hide_negative = fields.Boolean(string="Hide Negative Balance")
    limit_balance = fields.Float(string='Filter if balance is below', digits='Product Price')




    def print_report(self):
        """
         To get the date and print the report
         @return: return report
        """
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = self.read()
        res = res and res[0] or {}
        data.update({'form': res})
        return self.env.ref('analysis_reports.action_report_confirmation_of_balance').report_action(self, data=data)
