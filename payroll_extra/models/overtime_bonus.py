# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
import logging
import pytz
_logger = logging.getLogger(__name__)



class OvertimeBonusType(models.Model):
    _name = 'overtime.bonus.type'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
    _description = "Overtime Bonus Types"

    name = fields.Char(string='Name')
    rate = fields.Float(string="Rate")
    type = fields.Selection([('manual', 'Manual'),('wage', 'Wage'),('fixed', 'Fixed'),('deduction', 'Deduction'),], string='Incentive Type', required=True)

class OvertimeBonus(models.Model):
    _name = 'overtime.bonus'
    _description = "Overtime Bonus"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
    _order = "date_from desc, id desc"

    name = fields.Char(string='Description', tracking=True, required=True,)#states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]}
    date_from = fields.Datetime(string='Date', tracking=True, required=True,)#states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]},
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True,)#states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]}
    type = fields.Selection([('overtime', 'Overtime'),('bonus', 'Bonus'),('productivity', 'Productivity'),('deduction', 'Deduction'),], 'Type Category', default='overtime', readonly=False,)
    company_currency_id = fields.Many2one('res.currency', string="Report Company Currency", related='company_id.currency_id', readonly=True, tracking=True,)
    duration = fields.Float(string="Duration",tracking=True,)#states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]},
    amount = fields.Float(string="Quantity / Amount", tracking=True,)#,states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]}
    employee_id = fields.Many2one('hr.employee', string='Employee',  tracking=True, required=True,)#states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]},
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved'), ('rejected', 'Rejected')], string='State', required=True, default='draft', readonly=True, tracking=True,)
    department_id = fields.Many2one('hr.department', string="Department",related='employee_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', string="Job",related='employee_id.job_id', store=True)
    ot_amount = fields.Float(string="OT Amount", compute='_compute_amount', store=True)
    type_id = fields.Many2one('overtime.bonus.type', string='Type', required=True,)#states={'approved': [('readonly', True)], 'rejected': [('readonly', True)]},
    notes = fields.Text(string="Notes", readonly=True)


    @api.onchange('type_id')
    def _onchange_type_id(self):
        if self.type_id:
            self.type = self.type_id.type == 'fixed' and 'productivity' or (self.type_id.type == 'wage' and 'overtime' or (self.type_id.type == 'manual' and 'bonus' or 'deduction'))

    @api.depends('employee_id', 'amount','duration','type')
    def _compute_amount(self):
        DAYS_PER_MONTH = 365.0 / 12
        WORKING_TIME = 8
        for rec in self:
            if rec.type == 'overtime' and rec.employee_id.contract_id:
                rec.ot_amount = rec.employee_id.contract_id.wage / DAYS_PER_MONTH / WORKING_TIME * rec.duration
            elif rec.type == 'bonus':
                rec.ot_amount = rec.amount
            elif rec.type == 'productivity':
                rec.ot_amount =rec.amount * rec.type_id.rate
            elif rec.type == 'deduction':
                rec.ot_amount =-1*rec.amount
            else:
                rec.ot_amount = 0.0

    @api.constrains('date_from', 'employee_id')
    def _check_ot_bonus(self):
        for ot_bonus in self.filtered(lambda c: (c.state not in ['rejected'])):
            tz_name = self._context.get('tz') or self.env.user.tz or ot_bonus.employee_id.resource_calendar_id.tz
            context_tz = pytz.timezone(tz_name)
            tz_date_from = pytz.utc.localize(ot_bonus.date_from).astimezone(context_tz)
            domain = [
                ('id', '!=', ot_bonus.id),
                ('employee_id', '=', ot_bonus.employee_id.id),
                ('date_from', '>=', tz_date_from.replace(hour=0, minute=0, second=0)),
                ('date_from', '<=', tz_date_from.replace(hour=23, minute=59, second=59))]
            if self.search_count(domain):
                raise ValidationError(
                    _(
                        'An employee is limited to only one instance of overtime per day.\n\nEmployee: %(employee_name)s',
                        employee_name=ot_bonus.employee_id.name
                    )
                )

    @api.onchange('type')
    def check_val(self):
        for res in self:
            res.amount = res.duration = 0

    def unlink(self):
        for rec in self:
            if rec.state not in ['draft']:
                raise UserError(_('Only draft records can be deleted.'))
        return super(OvertimeBonus, self).unlink()

    def button_approve(self):
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no records to approve.'),
                'type': 'warning',
                'sticky': False},
        }
        filtered_recs = self.filtered(lambda s: s.state in ['draft',])
        if not filtered_recs:
            return notification
        for record in filtered_recs:
            record.write({'state': 'approved'})

    def button_reject(self):
        if self.state == 'draft':
            self.write({'state': 'rejected'})

    def set_to_draft(self):
        self.write({'state': 'draft'})

    def action_open_wizard(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("payroll_extra.overtime_bonus_form")
        action['res_id'] = self.id
        return action

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    overtime_line_ids = fields.One2many('overtime.bonus', 'employee_id', string='Overtime')

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _filter_contracts(self, contracts):
        contracts = super()._filter_contracts(contracts)
        payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        for employee_id in self.employee_ids:
            if self.env['overtime.bonus'].search([('employee_id', '=', employee_id.id),
                                                  ('date_from', '>=', payslip_run.date_start),
                                                  ('date_from', '<=', payslip_run.date_end),
                                                  ('state','=','draft')]):
                raise UserError(_("Please review and either approve or reject the draft overtime entries prior to generating the payslip."))
        return contracts

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: