# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ConfirmationOfBalance(models.AbstractModel):
    _name = 'report.analysis_reports.confirmation_of_balance_qweb'
    _description = 'Confirmation Of Balance'

    def amount_word(self, amount):
        """ Returns the data structure used by the template
        """
        return self.env.company.currency_id.amount_to_text(amount)
    def _get_balance(self,partner_ids,date):
        res = []
        where_params = [tuple(partner_ids), self.env.company.root_id.id, date]
        self._cr.execute("""SELECT account_move_line.partner_id, a.account_type, SUM(account_move_line.debit-account_move_line.credit)
                      FROM account_move_line
                      LEFT JOIN account_account a ON (account_move_line.account_id=a.id)
                      WHERE a.account_type IN ('asset_receivable','liability_payable')
                      AND account_move_line.partner_id IN %s AND
                      (("account_move_line"."parent_state" = 'posted') AND ("account_move_line"."company_id" = %s))
                      AND account_move_line.date <= %s
                      GROUP BY account_move_line.partner_id, a.account_type
                      """, where_params)
        for pid, type, val in self._cr.fetchall():
            res.append([pid, type, val])
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        date = data['form']['date']
        hide_negative = data['form']['hide_negative']
        limit_balance = data['form']['limit_balance']

        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        if data['form']['partner_id']:
            partner_ids = [data['form']['partner_id'][0]]
        else:
            self.env.cr.execute("""SELECT distinct l.partner_id from account_move_line l, account_move m where m.state='posted' and l.account_id in 
                (select id from account_account where account_type in ('asset_receivable','liability_payable')) and l.move_id = m.id and l.company_id in %s and l.partner_id is not NULL and l.date <= %s""", (tuple(data['context']['allowed_company_ids']),date))
            partner_ids = [partner_id[0] for partner_id in self.env.cr.fetchall()]

        docs = self.env['res.partner']
        docids=[]
        partner_data = []
        res=self._get_balance(partner_ids,date)
        for pid, type, val in res:
            if  (not hide_negative or val > 0) and limit_balance <= abs(val):
                docids.append(pid)
                partner = self.env['res.partner'].browse(pid)
                docs |= partner
                partner_data.append([partner,val])
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': docs,
            'partner_data':partner_data,
            'form':data['form'],
            'time': time,
            'company':self.env.company,
            'amount_word':self.amount_word,
        }
