# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import calendar

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CustomerStatementReport(models.AbstractModel):
    _name = 'report.analysis_reports.customer_statement_report_qweb'
    _description = 'Customer Collection Statement'

    def _get_invoices(self,partner_ids):
        result = {}
        for partner in partner_ids:
            res = []
            pdc_list = []
            gc_list = []
            others = []
            for line in partner.unreconciled_aml_ids.sorted(key=lambda i: (i.date_maturity or i.date, i.date , i.id)):
                if line.company_id != self.env.company:
                    continue
                if line.move_id.move_type in ('out_invoice','out_refund') and (line.amount_residual or line.amount_residual_currency):
                    res.append({'ref': line.move_id.name,
                                'date': line.date,
                                'due_date': line.date_maturity,
                                'communication':line.move_id.invoice_line_ids and (', '.join([x.name for x in line.move_id.invoice_line_ids])) or line.name,
                                'due_amount': line.amount_residual_currency if line.currency_id else line.amount_residual,})
                elif line.move_id.move_type == 'entry' and line.move_id.journal_id.type == 'bank'and (line.amount_residual or line.amount_residual_currency):
                    pdc_list.append({'ref': line.move_id.name,
                                'date': line.date,
                                'due_date': line.date_maturity,
                                'communication': line.name,
                                'due_amount': line.amount_residual_currency if line.currency_id else line.amount_residual,})
                elif (line.amount_residual or line.amount_residual_currency):
                    others.append({'ref': line.move_id.name,
                                'date': line.date,
                                'due_date': line.date_maturity,
                                'communication': line.name,
                                'due_amount': line.amount_residual_currency if line.currency_id else line.amount_residual,})
            for unposted_pdc in self.env['account.payment'].search([('guarantee_check','=',False),('partner_id','=',partner.id),('state','=','draft'),('payment_type','=','inbound')]):
                pdc_list.append({'ref': unposted_pdc.move_id and unposted_pdc.move_id.name or unposted_pdc.memo,
                                 'date': unposted_pdc.date,
                                 'due_date': unposted_pdc.date,
                                 'communication': unposted_pdc.name,
                                 'due_amount': -1*unposted_pdc.amount, })
            for guarantee_pdc in self.env['account.payment'].search([('guarantee_check','=',True),('partner_id','=',partner.id),('state','=','draft')]):
                gc_list.append({'ref': guarantee_pdc.move_id and guarantee_pdc.move_id.name or guarantee_pdc.name,
                                 'date': guarantee_pdc.date,
                                 'due_date': guarantee_pdc.date,
                                 'communication': guarantee_pdc.memo,
                                 'due_amount': guarantee_pdc.amount, })
            result[partner.id] = (res,pdc_list,others,gc_list)
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['res.partner'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
            'get_invoices': self._get_invoices(docs),
        }
