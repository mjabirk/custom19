# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models
import pytz
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class RawDataConsumption(models.TransientModel):

    _name = 'raw.data.consumption.analysis'
    _description = 'Raw Data Consumption'

    def _get_default_start_date(self):
        """ Get the default pickup date and make it extensible """
        user_tz = pytz.timezone(self.env.user.tz)
        return user_tz.localize(datetime.now().replace(day=1,hour=0, minute=0, second=0)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def _get_default_end_date(self):
        user_tz = pytz.timezone(self.env.user.tz)
        return user_tz.localize(datetime.now().replace(hour=23, minute=59, second=59)).astimezone(pytz.utc).strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    based_on = fields.Selection([('date','Date'),('delivery','Delivery Note')],string='Based On', default='delivery', required=True,
                                help="Date: System will filter the stock moves and raw data based on the date selected independently.\n\
                                     Delivery Note: System will filter delivery note based on the date and then search for the raw data for those delivery note.")
    start_date = fields.Datetime(string='Start Date', required=True, default=_get_default_start_date)
    end_date = fields.Datetime(string='End Date', required=True, default=_get_default_end_date)

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
        return self.env.ref('productivity_report.action_report_consumption').report_action(self, data=data)
