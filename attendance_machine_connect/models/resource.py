# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    allowed_late_time = fields.Float("Allowed Late Time (Minutes)", default=5, )
    allowed_leave_early_time = fields.Float("Allowed Leave Early Time (Minutes)", default=5)
    in_beginning_time = fields.Float("Punch In Beginning Time (Minutes)", default=60,help='All attendance record before this much minutes than planned time will not be considered for punch in.')
    in_ending_time = fields.Float("Punch In Ending Time (Minutes)", default=0,help='All attendance record after this much minutes than planned time will not be considered for punch in.')
    out_beginning_time = fields.Float("Punch Out Beginning Time (Minutes)", default=0,help='All attendance record before this much minutes than planned time will not be considered for punch out.')
    out_ending_time = fields.Float("Punch Out Ending Time (Minutes)", default=120,help='All attendance record after this much minutes than planned time will not be considered for punch out.')
    update_work_entry = fields.Boolean('Generate Time-Off', default=False,help='Generate time off based on attendance.')
    allow_overtime = fields.Boolean('Allow Overtime', default=False)
    consider_overtime = fields.Float('Consider Overtime if time over (Minutes)', default=60, help='Over time will be calculated only if employee worked extra more than this much time')
    free_timing = fields.Boolean('Free Timing', help="System will generate attendance without considering employee's working time schedule")