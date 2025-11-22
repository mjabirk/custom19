# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _


class ConfirmationBalanceWizard(models.TransientModel):
    _name = 'deferred.details.wizard'
    _description = 'Deferred Details'

    date = fields.Date(string='Report Date', required=True, default=fields.Date.today())
    rec_type = fields.Selection(selection=[('expenses', 'Expenses'),('revenues', 'Revenues'),('all', 'All'),], required=True, default='expenses')
    hide_zero = fields.Boolean(string="Hide if Balance is 0", default=True)


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
        return self.env.ref('analysis_reports.action_report_deferred_details').report_action(self, data=data)
