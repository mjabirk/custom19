# -*- coding:utf-8 -*-

from odoo import api, models, _, fields
from odoo.exceptions import UserError
from operator import itemgetter
from dateutil.relativedelta import relativedelta


class ReportEmpProd(models.AbstractModel):
    _name = 'report.productivity_report.report_empproductivityanalysis'
    _description = "Employee Productivity Analysis"
    def get_employee(self, form):
        tot_for_day = {'name':'Total','total':0}
        employee_list = {}
        previous_month = form.get('previous_month', [])
        productivity_type = form.get('productivity_type', [])
        if previous_month:
            first_date = fields.Date.today() - relativedelta(day=1,months=1)
        else:
            first_date = fields.Date.today() + relativedelta(day=1)
        current_month = first_date.strftime('%m')
        if productivity_type == 'trips':
            query = """select x_employee_id, sum(x_trips) from x_productivity_record 
                        WHERE x_date >= %s and x_date <= %s  and x_calculation_type = 'trips' group by x_employee_id"""
        else:
            query = """select x_employee_id, sum(x_quantity )  from x_productivity_record 
                        WHERE x_date >= %s and x_date <= %s  and x_calculation_type = 'quantity' group by x_employee_id"""
        for days_add in range(31):
            current_date = first_date + relativedelta(days=days_add)
            if current_date.strftime('%m') != current_month:
                break
            self._cr.execute(query, (current_date, current_date))
            for employee_id, quantity in self._cr.fetchall():
                if employee_id:
                    if employee_id in employee_list:
                        employee_list[employee_id][days_add] = quantity
                        employee_list[employee_id]['total'] += quantity
                        tot_for_day[days_add] = quantity + tot_for_day.get(days_add, 0)
                        tot_for_day['total'] += quantity
                    else:
                        employee = self.env['hr.employee'].browse(employee_id)
                        employee_list[employee_id] = {'name':employee.name, days_add:quantity, 'total':quantity}
                        tot_for_day[days_add] = quantity + tot_for_day.get(days_add, 0)
                        tot_for_day['total'] += quantity
        ret_value = list(employee_list.values())
        ret_value = sorted(ret_value, key=itemgetter('total'),reverse=True)
        ret_value.append(tot_for_day)

        return ret_value
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_employee = self.get_employee(data['form'])
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_employee': get_employee,
        }
