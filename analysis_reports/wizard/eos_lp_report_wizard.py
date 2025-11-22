# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _


class EOSLPWizard(models.TransientModel):
    _name = 'eoslp.wizard'
    _description = 'EOS LP'

    batch_id = fields.Many2one('hr.payslip.run', string='Payslip Batch')


    def print_report(self):
        """
         To get the date and print the report
         @return: return report
        """
        self.ensure_one()
        data = {'ids': self.env.context.get('active_ids', [])}
        res = {'batch_id':self.batch_id.id}
        data.update({'form': res})
        return self.env.ref('analysis_reports.action_eos_lp_report').report_action(self, data=data)
