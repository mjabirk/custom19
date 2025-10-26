# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import logging
import pytz
_logger = logging.getLogger(__name__)


class OvertimeBonus(models.Model):
    _inherit = 'overtime.bonus'
    notes = fields.Text(string="Notes", readonly=True)
    trips = fields.Float(string="Trips",readonly=True)
    rate = fields.Float(string="Rate",readonly=True)
    from_raw_data = fields.Boolean(string='Generated from raw data', default=False, readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', readonly=True)
    calculation_type = fields.Selection([('trips', 'Trips'),('quantity', 'Quantity')], 'Calculation Based on', default='quantity', readonly=True,)

    @api.depends('employee_id', 'amount','duration','type','trips','rate','calculation_type')
    def _compute_amount(self):
        DAYS_PER_MONTH = 365.0 / 12
        WORKING_TIME = 8
        for rec in self:
            if rec.type == 'overtime' and rec.employee_id.contract_id:
                rec.ot_amount = rec.employee_id.contract_id.wage / DAYS_PER_MONTH / WORKING_TIME * rec.duration
            elif rec.type == 'bonus':
                rec.ot_amount = rec.amount
            elif rec.type == 'deduction':
                rec.ot_amount =-1*rec.amount
            elif rec.type == 'productivity':
                if rec.from_raw_data:
                    rec.ot_amount = rec.calculation_type == 'trips' and rec.trips * rec.rate or rec.amount * rec.rate
                else:
                    rec.ot_amount =rec.amount * rec.type_id.rate
            else:
                rec.ot_amount = 0.0

    @api.constrains('date_from', 'employee_id')
    def _check_ot_bonus(self):
        print('inside _check_ot_bonus')
        for ot_bonus in self.filtered(lambda c: (c.state not in ['rejected'])):
            print(1111)
            if not ot_bonus.from_raw_data:
                print(2222)
                tz_name = self._context.get('tz') or self.env.user.tz or ot_bonus.employee_id.resource_calendar_id.tz
                context_tz = pytz.timezone(tz_name)
                tz_date_from = pytz.utc.localize(ot_bonus.date_from).astimezone(context_tz)
                domain = [
                    ('id', '!=', ot_bonus.id),
                    ('from_raw_data','=',False),
                    ('employee_id', '=', ot_bonus.employee_id.id),
                    ('date_from', '>=', tz_date_from.replace(hour=0, minute=0, second=0)),
                    ('date_from', '<=', tz_date_from.replace(hour=23, minute=59, second=59))]
                if self.search_count(domain)>0:
                    print(3333)
                    raise ValidationError(
                        _(
                            f'An employee is limited to only one instance of overtime per day.\nEmployee: %(employee_name)s Duplicate of %(ot_bonus_id)s Date %(date_ot)s',
                            employee_name=ot_bonus.employee_id.name,ot_bonus_id=ot_bonus.id,date_ot=ot_bonus.date_from
                        )
                    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: