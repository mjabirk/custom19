# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError
#from datetime import datetime
from operator import itemgetter

class EOSLP(models.AbstractModel):
    _name = 'report.analysis_reports.eos_lp_report'
    _description = 'Accumulated EOS and LP'


    def _get_details(self, batch_id):
        res = []
        batch = self.env['hr.payslip.run'].browse(batch_id)
        for payslip in batch.slip_ids:
            lp = eos = 0
            for line in payslip.line_ids:
                if line.name == 'Leave Pay' or line.code == 'LPAC':
                    lp = line.total
                elif line.name == 'EOS' or line.code == 'EOSAC':
                    eos = line.total
            if lp or eos:
                res.append({'employee_name': payslip.employee_id.name or '',
                        'employee_id': payslip.employee_id.identification_id,
                        'lp_amount': lp,
                        'eos_amount': eos,
                        })
        res = sorted(res, key=itemgetter('employee_name'))
        return res
        #
        #
        #
        # contracts = self.env['hr.contract'].search(['|', ('active','=',True), ('active','=',False), ('date_start', '<', date), '|',('date_end', '>', date),('date_end', '=', False)])
        # for contract in contracts:
        #     date_to = datetime.strptime(date, '%Y-%m-%d').date()
        #     # if not contract or contract.date_start > date_to:
        #     #     contract = self.env['hr.contract'].search([('employee_id', '=', employee.id),('date_start', '<', date),], limit=1, order='date_start desc')
        #     # if not contract:
        #     #     continue
        #     date_from = contract.date_start
        #     print(date_to, date_from, contract.employee_id.name, contract.name,'====================')
        #     delay = (date_to - date_from).days + 1
        #     unpaid_leaves = self.env['hr.leave'].search([('employee_id', '=', contract.employee_id.id), ('state', '=', 'validate'), ('request_date_from', '>=', date_from),
        #          ('request_date_from', '<=', date_to), ('holiday_status_id.name', 'in', ['Unpaid', 'Absent'])])
        #     unpaid_days = tot_unpaid_days = 0
        #     for unpaid_leave in unpaid_leaves:
        #         unpaid_days += unpaid_leave.number_of_days
        #     tot_unpaid_days = unpaid_days
        #     if unpaid_days > 15:
        #         unpaid_days -= 15
        #     else:
        #         unpaid_days = 0
        #
        #     if delay <= unpaid_days:
        #     if delay <= unpaid_days:
        #         delay = 0
        #     else:
        #         delay = delay - unpaid_days
        #     eos_amount = round((contract.wage  * contract.eos_days * 12 * delay / (365 * 365)) or 0)
        #
        #     total_taken_days = 0
        #     annual_leaves_taken = self.env['hr.leave'].search(
        #         [('employee_id', '=', contract.employee_id.id), ('state', '=', 'validate'),
        #          ('request_date_from', '<', date_to), ('request_date_from', '>=', date_from),
        #          ('holiday_status_id.name', 'in', ['Annual'])], order='request_date_from desc')
        #     for annual_leave in annual_leaves_taken:
        #         total_taken_days += annual_leave.number_of_days
        #
        #     delay = (date_to - date_from).days - tot_unpaid_days + 1
        #     lp_amount = round((contract.leave_pay_days * (delay / 365) - total_taken_days) * (
        #                 contract.wage + contract.accommodation_allowance) * 12 / 365) or 0
        #
        #     res.append({'employee_name':contract.employee_id.name or '',
        #                 'employee_id':contract.employee_id.identification_id,
        #                 'lp_amount':lp_amount,
        #                 'eos_amount': eos_amount,
        #                 })
        # res = sorted(res, key=itemgetter('employee_name'))
        # return res

    @api.model
    def _get_report_values(self, docids, data=None):
        batch_id = data['form']['batch_id']
        batch = self.env['hr.payslip.run'].browse(batch_id)
        if not data.get('form'):
            raise UserError(_("Generate this report from Accounts/Reporting menu."))

        return {
            'doc_ids': data['ids'],
            'doc_model': 'eoslp.wizard',
            'form':data['form'],
            'acc_eos_lp': self._get_details(batch_id),
            'time': time,
            'date_end':batch.date_end,
            'company':self.env.company,
        }