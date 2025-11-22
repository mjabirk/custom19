# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DeferredDetails(models.AbstractModel):
    _name = 'report.analysis_reports.deferred_details_qweb'
    _description = 'Deferred Details'


    def _get_expenses(self, date, rec_type, hide_zero=True):
        res = []
        if rec_type == 'revenues':
            return res
        d_expenses = self.env['account.asset'].search([('asset_type', '=', 'expense'), ('state', '!=', 'model'), ('parent_id', '=', False),('acquisition_date','<=',date)])
        for expense in d_expenses:
            depreciated_amount = 0
            for entries in expense.depreciation_move_ids:
                print(entries.date,date,type(entries.date),type(date),'=-================')
                if entries.date.strftime("%Y-%m-%d") <= date:
                    depreciated_amount += entries.amount_total_signed
            balance = expense.original_value - depreciated_amount
            if not hide_zero or abs(balance) > .01:
                name = ''
                name_list = []
                for move_line in  expense.original_move_line_ids:
                    if move_line.move_id and name and move_line.move_id.name not in name_list:
                        name += ', '+ move_line.move_id.name
                        name_list.append(move_line.move_id.name)
                    elif move_line.move_id:
                        name = move_line.move_id.name
                        name_list.append(move_line.move_id.name)

                res.append({'related_entry':name,
                            'description':expense.name,
                            'original':expense.original_value,
                            'date': expense.acquisition_date,
                            'depreciation':depreciated_amount,
                            'balance':balance,
                            })
        return res

    def _get_revenues(self, date, rec_type, hide_zero=True):
        res = []
        if rec_type == 'expenses':
            return res
        d_expenses = self.env['account.asset'].search([('asset_type', '=', 'sale'), ('state', '!=', 'model'), ('parent_id', '=', False), ('acquisition_date', '<=', date)])
        for expense in d_expenses:
            depreciated_amount = 0
            for entries in expense.depreciation_move_ids:
                if entries.date <= date:
                    depreciated_amount += entries.amount_total_signed
            balance = expense.original_value - depreciated_amount
            if not hide_zero or abs(balance) > .01:
                name = ''
                name_list = []
                for move_line in expense.original_move_line_ids:
                    if move_line.move_id and name and (move_line.move_id.name not in name_list):
                        name += ', ' + move_line.move_id.name
                        name_list.append(move_line.move_id.name)
                    elif move_line.move_id:
                        name = move_line.move_id.name
                        name_list.append(move_line.move_id.name)

                res.append({'related_entry': name,
                            'description': expense.name,
                            'date': expense.acquisition_date,
                            'original': expense.original_value,
                            'depreciation': depreciated_amount,
                            'balance': balance,
                            })
        return res

    @api.model
    def _get_report_values(self, docids, data=None):
        date = data['form']['date']
        hide_zero = data['form']['hide_zero']
        rec_type = data['form']['rec_type']

        if not data.get('form'):
            raise UserError(_("Generate this report from Accounts/Reporting menu."))

        return {
            'doc_ids': data['ids'],
            'doc_model': 'deferred.details.wizard',
            'form':data['form'],
            'deferred_expenses': self._get_expenses(date, rec_type, hide_zero),
            '_get_revenues': self._get_revenues(date, rec_type, hide_zero),
       #     'docs': docs,
            'time': time,
            'company':self.env.company,
        }
