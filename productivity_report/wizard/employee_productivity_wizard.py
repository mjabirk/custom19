# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class EmpProductivityAnalysis(models.TransientModel):

    _name = 'employee.productivity.analysis'
    _description = 'Employee Productivity Analysis'


    def _get_default_start_date(self):
        year = fields.Date.from_string(fields.Date.today()).strftime('%Y')
        month = fields.Date.from_string(fields.Date.today()).strftime('%m')
        return '{}-{}-01'.format(year,month)

    def _get_default_end_date(self):
        date = fields.Date.from_string(fields.Date.today())
        return date.strftime('%Y') + '-' + date.strftime('%m') + '-' + date.strftime('%d')

    previous_month = fields.Boolean(string='Previous Month', default=False)
    productivity_type = fields.Selection([('trips', 'Trips'), ('quantity', 'Quantity')], string='Type', required=True, default='trips')

    start_date = fields.Date(string='Start Date', required=True, default=_get_default_start_date)
    end_date = fields.Date(string='End Date', required=True, default=_get_default_end_date)

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
        return self.env.ref('productivity_report.action_report_productivity').report_action(self, data=data)
