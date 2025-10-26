# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

from odoo import api, fields, models, _
from odoo.fields import Datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare

class HrLeave(models.Model):
    _inherit = 'hr.leave'

    notice_period = fields.Integer( string='Notice Period', copy=False, default=1)
    add_description = fields.Boolean( string='Add Description on Termination Letter', copy=False, default=1)
    air_ticket = fields.Float('Air Ticket Amount(QR)', default=0, tracking=True, readonly=False, copy=False)
