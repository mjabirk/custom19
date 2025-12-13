# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import datetime, timedelta, date
from operator import itemgetter

import pytz
from odoo import models
from odoo import fields
from odoo import api
from odoo import exceptions, _
from odoo.tools import format_datetime
from odoo.osv.expression import AND, OR
from odoo.tools.float_utils import float_is_zero


class HrAttendance(models.Model):
    _name = "hr.attendance.analysis"
    _description = "Attendance Hours Analysis"
    _order = "rec_date desc"

    department_id = fields.Many2one('hr.department', string="Department", readonly=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", readonly=True)
    company_id = fields.Many2one('res.company', string="Company", readonly=True)
    rec_date = fields.Date("Date", readonly=True)
    total_hours = fields.Float("Hours Worked", readonly=True)
    extra_hours = fields.Float("Extra Hours", readonly=True)
    delay_hours = fields.Float("Delay", readonly=True)
    early_leaving_hours = fields.Float("Early Leaving", readonly=True)
    absent_hours = fields.Float("Absent Hours", readonly=True)
    def generate_analysis_data(self):
        emp_ids = self.env['hr.employee'].search([('contract_id', '!=', False), ('contract_id.state', '=', 'open')])
        yesterday = date.today() - timedelta(days = 1)
        utc = pytz.UTC
        for employee in emp_ids:
            tz_name = employee.resource_calendar_id.tz or self._context.get('tz') or self.env.user.tz
            context_tz = pytz.timezone(tz_name)
            yesterday_start = context_tz.localize(
                datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=1, seconds=1)).astimezone(pytz.utc)
            yesterday_end = context_tz.localize(
                datetime.now().replace(hour=23, minute=59, second=59) - timedelta(days=1)).astimezone(pytz.utc)
            res = employee.resource_calendar_id._attendance_intervals_batch(yesterday_start, yesterday_end, employee.resource_id)
            total_hours = extra_hours = delay_hours = early_leaving_hours = absent_hours = 0
            att_list = []
            for date_from, date_to, resource in res[employee.resource_id.id]:
                if resource and (resource.work_entry_type_id and resource.work_entry_type_id.code != 'PAIDLEAVE106' or not resource.work_entry_type_id):
                    attendance = self.env['hr.attendance'].search([('employee_id', '=', employee.id),
                                                                   ('check_in', '<=', date_to.astimezone(utc)),
                                                                   ('check_out', '>=', date_from.astimezone(utc)),
                                                                   ('id', 'not in', att_list),
                                                                   ], limit=1)
                    if attendance and attendance.check_out:
                        total_hours += attendance.worked_hours
                        extra_hours =(attendance.check_out - attendance.check_in).seconds/3600 - (date_to - date_from).seconds/3600
                        if extra_hours < 0:
                            extra_hours = 0
                        early_leaving_hours +=date_to.astimezone(utc) > utc.localize(attendance.check_out) and (date_to.astimezone(utc) - utc.localize(attendance.check_out)).seconds/3600 or 0
                        delay_hours += date_from.astimezone(utc) < utc.localize(attendance.check_in) and (utc.localize(attendance.check_in) - date_from.astimezone(utc)).seconds/3600 or 0
                        att_list.append(attendance.id)
                    else:
                        absent_hours = (date_to - date_from).seconds/3600
            duplicate_rec = self.search([('employee_id','=',employee.id),
                                         ('rec_date','=',yesterday)])
            if duplicate_rec:
                duplicate_rec.unlink()
            if total_hours or extra_hours or delay_hours or early_leaving_hours or absent_hours:
                self.create({'employee_id':employee.id,
                             'rec_date':yesterday,
                             'department_id':employee.department_id.id,
                             'company_id':employee.company_id.id,
                             'total_hours':total_hours,
                             'extra_hours':extra_hours,
                             'delay_hours':delay_hours,
                             'early_leaving_hours':early_leaving_hours,
                             'absent_hours':absent_hours
                })
        return True

