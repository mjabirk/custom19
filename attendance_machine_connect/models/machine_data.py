# -*- coding: utf-8 -*-

from odoo import api, models, fields
from datetime import datetime, timedelta
import pytz

import logging
_logger = logging.getLogger(__name__)

WEEK_DAY = {'Monday':'0',
            'Tuesday':'1',
            'Wednesday':'2',
            'Thursday':'3',
            'Friday':'4',
            'Saturday':'5',
            'Sunday':'6',}

class AttendanceMachines(models.Model):
    _name = 'attendance.machines'
    _description = "Attendance Machines"

    name = fields.Char(string='Name')
    ip = fields.Char(string='IP Address')
    port = fields.Integer(string='Port',default=4370)
    model = fields.Selection([('zkteco', 'ZKTeco'),], 'Machine Model', default='zkteco')
    processing = fields.Boolean(string='Fetching Data',readonly=True)
    info = fields.Text(string='Info', readonly=True)
    last_rec_date = fields.Datetime(string='Uploaded Till',readonly=False)
    active = fields.Boolean(default=True)


class AttendanceMachineData(models.Model):
    _name = 'attendance.machine.data'
    _description = "Attendance Machine Data"
    name = fields.Char(string='Attendance Machine')
    ip_address = fields.Char(string='Attendance Machine IP')
    type = fields.Char(string='Type')
    date = fields.Datetime(string='Time')
    uid = fields.Char(string='ID')
    barcode = fields.Char(string='Badge ID')
    status = fields.Char(string='Status', readonly=True)
    processed = fields.Boolean(string='Processed')

    def process_punching_time(self, punch_time, resource_calendar_id):
        week_day = WEEK_DAY[punch_time.strftime('%A')]
        in_time_before = in_time_after = out_time_before = out_time_after = 0

        if resource_calendar_id.in_beginning_time > 0:
            in_time_before = resource_calendar_id.in_beginning_time
        if resource_calendar_id.in_ending_time > 0:
            in_time_after = resource_calendar_id.in_ending_time
        if resource_calendar_id.out_beginning_time > 0:
            out_time_before = resource_calendar_id.out_beginning_time
        if resource_calendar_id.out_ending_time > 0:
            out_time_after = resource_calendar_id.out_ending_time
        calendar_lines = self.env['resource.calendar.attendance'].search([('calendar_id','=',resource_calendar_id.id),('dayofweek','=',week_day)])
        from_times = []
        to_times = []
        check_in_times = []
        check_out_times = []
        for calendar_line in calendar_lines:
            from_times.append((calendar_line.hour_from-in_time_before/60,max(calendar_line.hour_from+in_time_after/60,calendar_line.hour_from+resource_calendar_id.allowed_late_time/60),calendar_line.hour_from))
            to_times.append((min(calendar_line.hour_to-out_time_before/60,calendar_line.hour_to-resource_calendar_id.allowed_leave_early_time/60),calendar_line.hour_to+out_time_after/60,calendar_line.hour_to))
        punch_time = int(punch_time.strftime('%H'))+int(punch_time.strftime('%M'))/60
        for from_time in from_times:
            if from_time[0] <= punch_time and from_time[1] >= punch_time:
                if resource_calendar_id.allowed_late_time and punch_time>from_time[2] and punch_time-resource_calendar_id.allowed_late_time/60 <= from_time[2]:
                    check_in_times.append(from_time[2])
                else:
                    check_in_times.append(punch_time)
        for to_time in to_times:
            if to_time[0] <= punch_time and to_time[1] >= punch_time:
                if resource_calendar_id.allowed_leave_early_time and punch_time < to_time[2] and punch_time + resource_calendar_id.allowed_leave_early_time / 60 >= to_time[2]:
                    check_out_times.append(to_time[2])
                else:
                    check_out_times.append(punch_time)
        return({'In Times':check_in_times,'Out Times':check_out_times})


    def create_timesheet(self):
        # Delete duplicates
        punch_datas = self.search([('processed', '=', False)], order='date')
        deleted_ids = []
        for punch_data in punch_datas:
            if punch_data.id not in deleted_ids:
                duplicate_ids = self.search([('id', '!=',punch_data.id),
                                             ('date','=',punch_data.date),
                                             ('barcode','=',punch_data.barcode)], order='date')
                for duplicate_id in duplicate_ids:
                    if duplicate_id.processed:
                        deleted_ids.append(punch_data.id)
                        punch_data.unlink()
                        break
                    else:
                        deleted_ids.append(duplicate_id.id)
                        duplicate_id.unlink()
        punch_datas = self.search([('processed', '=', False)], order='date')
        #Create timesheet from punch data
        for punch_data in punch_datas:
            employee_id = self.env['hr.employee'].search([('barcode', '=', punch_data.barcode)], order="company_id, name",limit=1)
            if not employee_id and len(punch_data.barcode) == 9:
                all_employee_id = self.env['hr.employee'].search([('barcode', 'ilike', punch_data.barcode)], order="company_id, name")
                for employee in all_employee_id:
                    if employee.barcode[1:] == punch_data.barcode:
                        employee_id = employee
                        break
            if employee_id and punch_data.date:
                tz_name = self._context.get('tz') or self.env.user.tz or employee_id.resource_calendar_id.tz
                context_tz = pytz.timezone(tz_name)
                punch_time = pytz.utc.localize(punch_data.date, is_dst=False).astimezone(context_tz)
                new_attenance = self.env['hr.attendance'].search([('employee_id', '=', employee_id.id), '|',('check_in', '>=', punch_data.date),('check_out', '>=', punch_data.date)], order='check_in desc', limit=1)
                if new_attenance:
                    #Ignore this punch because there is new attendance after this
                    continue

                old_attenance = self.env['hr.attendance'].search([('employee_id', '=', employee_id.id), ('check_in', '<=', punch_data.date),('check_out', '=', False)], order='check_in desc', limit=1)
                #if employee_id.resource_calendar_id.free_timing:
                # if old_attenance:
                #     old_attenance.check_out = punch_data.date
                #    Command above line and uncommand below 5 lines if need to restrict punching in and out only for same day. TODO: Need to consider timezone in below code

                if old_attenance.check_in and (old_attenance.check_in.strftime('%Y%m%d') == punch_data.date.strftime('%Y%m%d')):
                    old_attenance.check_out = punch_data.date
                else:
                    old_attenance.unlink()
                    self.env['hr.attendance'].create({'employee_id': employee_id.id, 'check_in': punch_data.date, })
                # else:
                #     self.env['hr.attendance'].create({'employee_id': employee_id.id,'check_in': punch_data.date,})
                # else:
                #     processed_time = self.process_punching_time(punch_time,employee_id.resource_calendar_id)
                #     if employee_id.id == 512:
                #         print(processed_time,'processed_time')
                #     create_new_attendance = True
                #     old_deleted = False
                #     if old_attenance:
                #         if old_attenance.check_in.strftime('%Y%m%d') == punch_time.strftime('%Y%m%d'):
                #             if processed_time['Out Times']:
                #                 old_attenance.write({'check_out':context_tz.localize(old_attenance.check_in.replace(hour=0,minute =0,second=0)+timedelta(hours=processed_time['Out Times'][0])).astimezone(pytz.utc).replace(tzinfo=None)})
                #                 create_new_attendance=False
                #         else:
                #             old_attenance.unlink()
                #             old_deleted = True
                #     if create_new_attendance and processed_time['In Times']:
                #         if old_attenance and not old_deleted:
                #             old_attenance.unlink()
                #         self.env['hr.attendance'].create({'employee_id': employee_id.id, 'check_in': context_tz.localize(punch_data.date.replace(hour=0, minute=0, second=0)+timedelta( hours=processed_time['In Times'][0])).astimezone(pytz.utc).replace(tzinfo=None)})
            punch_data.write({'processed':True})

        return {}


    def create_timeoff(self):
        employee_ids = self.env['hr.employee'].search([('resource_calendar_id.update_work_entry','=',True)])
        for employee in employee_ids:
            tz_name = employee.resource_calendar_id.tz or self._context.get('tz') or self.env.user.tz
            context_tz = pytz.timezone(tz_name)
            yesterday_start = context_tz.localize(datetime.now().replace(hour=0,minute =0,second=0) - timedelta(days=1,seconds=1)).astimezone(pytz.utc)
            yesterday_end = context_tz.localize(datetime.now().replace(hour=23, minute=59, second=59) - timedelta(days=1)).astimezone(pytz.utc)
            if employee.contract_id.state != 'open' or employee.contract_id.date_start > yesterday_start.date() or employee.contract_id.date_end < yesterday_start.date():
                continue

            paid_time_off_type = self.env['hr.leave.type'].search([('request_unit', '=', 'hour'), '|', ('company_id', '=', employee.company_id.id),('company_id', '=', False), ('work_entry_type_id.code', '=', 'Unpaid')])
            attendance_ids = self.env['hr.attendance'].search([('employee_id','=',employee.id),('check_in','>=', yesterday_start),('check_out','<',yesterday_end)])
            att_intervals = employee.resource_calendar_id._attendance_intervals_batch(yesterday_start,yesterday_end)[False]

            if att_intervals and paid_time_off_type:
                for start, stop, meta in att_intervals:
                    if meta.dayofweek != '4':
                        found = False
                        for attendance in attendance_ids:
                            if attendance.check_out and stop.astimezone(pytz.utc).strftime('%Y%m%d_%H%M%S') >= attendance.check_in.strftime('%Y%m%d_%H%M%S') and start.astimezone(pytz.utc).strftime('%Y%m%d_%H%M%S') <= attendance.check_out.strftime('%Y%m%d_%H%M%S') and attendance.worked_hours:
                                found = True
                        if not found:
                            check_duplicate = self.env['hr.leave'].search([('employee_id','=',employee.id),
                                                                         #  ('holiday_status_id','=',paid_time_off_type[0].id),
                                                                           ('request_date_from','<=',start.strftime('%Y-%m-%d')),
                                                                           ('request_date_to','>=',start.strftime('%Y-%m-%d')),
                                                                         #  ('request_hour_from','=',int(start.strftime('%M')) >5 and '%s.5'%(int(start.strftime('%H'))) or '%s'%int(start.strftime('%H'))),
                                                                           ('state','not in',('refuse','cancel')),])

                            if not check_duplicate:
                                try:
                                    leave_id = self.env['hr.leave'].create({
                                        'name': 'No proper records of attendance were found this day. Kindly assess the employee\'s attendance, make necessary time adjustments, and then approve or decline the time-off request.',
                                        'employee_id': employee.id,
                                        'holiday_status_id': paid_time_off_type[0].id,
                                        'request_unit_hours':False,
                                        'request_unit_half':False,
                                        'request_date_from':start.replace(tzinfo=None),#.replace(tzinfo=pytz.utc),
                                        'request_date_to':start.replace(tzinfo=None),#.replace(tzinfo=pytz.utc),
                                        # 'request_hour_from': int(start.strftime('%M')) >5 and '%s.5'%(int(start.strftime('%H'))) or '%s'%int(start.strftime('%H')),
                                        # 'request_hour_to': int(stop.strftime('%M')) >5 and '%s.5'%(int(stop.strftime('%H'))) or '%s'%int(stop.strftime('%H')),
                                        'date_from':start.replace(tzinfo=None),
                                        'date_to':stop.replace(tzinfo=None),

                                    })
                                    leave_id._compute_date_from_to()
                                except Exception as e:
                                    _logger.debug(f'Unable to createno attendance time-off for {employee.name} on {start.strftime("%Y-%m-%d")} because of {e}.')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: