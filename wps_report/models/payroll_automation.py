# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class PayrollAutomation(models.Model):
    _name = 'payroll.automation'
    _description = 'Payroll Automation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True  # Ensures multi-company compatibility

    # Fields
    name = fields.Char(string='Name', required=True, tracking=True)

    employee_department_ids = fields.Many2many(
        'hr.department',
        string='Employee Departments',
        help='Select the employee departments for which payroll automation applies.',
        tracking=True
    )

    schedule_date = fields.Date(
        string='Scheduled Date',
        required=True,
        tracking=True,
        help='The date on which payroll automation should be scheduled.'
    )

    last_created_date = fields.Datetime(
        string='Last Created Date',
        default=fields.Datetime.now,
        tracking=True,
        help='Date and time when the payroll automation was last created or triggered.'
    )

    active = fields.Boolean(
        string='Active',
        default=True,
        help='Activate or deactivate payroll automation.'
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        help='Company associated with this payroll automation',
        tracking=True
    )

    bank_list = fields.Selection([
        ('hsb', 'HSBC Bank Middle East'),
        ('mar', 'Masraf Al Rayyan Bank'),
        ('qnb', 'Qatar National Bank'),
        ('cbq', 'Commercial Bank of Qatar')],
        string='WPS Bank', required=True,default='qnb')

    email = fields.Char('Email send to')

    structure_id = fields.Many2one(
        'hr.payroll.structure',
        string='Structure',
        tracking=True
    )

    batch_name = fields.Char('Batch Name')


    _sql_constraints = [
        ('name_unique', 'unique(name, company_id)', 'The payroll automation name must be unique within a company!'),
    ]
    def action_trigger_payroll(self):
        automations = self.search([('active','=',True)])
        for automation in automations:
            self = self.with_context(allowed_company_ids=[automation.company_id.id])
            if not automation.schedule_date:
                automation.schedule_date = datetime.date.today()
            if automation.schedule_date == fields.Date.today():
                first_day_of_current_month = (fields.Datetime.now().replace(day=1)).date()
                date_end = first_day_of_current_month - timedelta(days=1)
                date_start = date_end.replace(day=1)
                company_code = ''.join([word[0].upper() for word in automation.company_id.name.split(' ') if word])[:2]

                payslip_run = self.env['hr.payslip.run'].create([
                    {
                        'name': date_start.strftime(automation.batch_name) + company_code,
                        'date_start': date_start,
                        'date_end': date_end,
                        'company_id': automation.company_id.id,
                    }])
                domain = [('contract_ids.state', 'in', ('open', 'close')), ('company_id', '=', automation.company_id.id)]
                if automation.employee_department_ids:
                    domain.append(('department_id','in',automation.employee_department_ids.ids))
                employees = self.env['hr.employee'].search(domain)
                contracts = employees._get_contracts(date_start, date_end, states=['open', 'close']).filtered(
                    lambda c: c.active)
                contracts.generate_work_entries(date_start, date_end)
                # work_entries = self.env['hr.work.entry'].search([
                #     ('date_start', '<=', date_end + datetime.timedelta(days=1)),
                #     ('date_stop', '>=', date_start + datetime.timedelta(days=-1)),
                #     ('employee_id', 'in', employees.ids), ])
                # payslip_work_entries._check_undefined_slots(slip.date_from, slip.date_to)
                Payslip = self.env['hr.payslip']
                default_values = Payslip.default_get(Payslip.fields_get())
                payslips_vals = []
                for contract in contracts:
                    values = dict(default_values, **{
                        'name': 'New Payslip',
                        'employee_id': contract.employee_id.id,
                        'payslip_run_id': payslip_run.id,
                        'date_from': payslip_run.date_start,
                        'date_to': payslip_run.date_end,
                        'contract_id': contract.id,
                        'struct_id': automation.structure_id and automation.structure_id.id or contract.structure_type_id.default_struct_id.id,
                    })
                    payslips_vals.append(values)
                payslips = Payslip.with_context(tracking_disable=True).create(payslips_vals)
                payslips._compute_name()
                payslips.compute_sheet()
                payslip_run.action_validate()
                payslip_run.move_id and payslip_run.move_id.action_post()
                # Create email
                if automation.email:
                    sheet_wiz = self.env['salary.transfer.sheet'].generate_transfer_sheet(given_payroll_reg = payslip_run, wps_bank = automation.bank_list)
                    attachment_id = self.env['ir.attachment'].create({
                        'name': sheet_wiz[0],
                        'type': 'binary',
                        'datas': sheet_wiz[1],
                        'res_model': 'mail.mail',
                        'res_id': 0,
                        'mimetype': 'text/plain',
                    })
                    mail_id = self.env['mail.mail'].create({
                        'subject': f'{automation.company_id.name} WPS File of {date_start.strftime("%Y%m")}',
                        'email_to': automation.email,
                        'body_html': 'WPS file',
                        'attachment_ids': [(4, attachment_id.id)],  # Attach the file
                    })
                    # Send email
                    mail_id.send()
                automation.schedule_date = automation.schedule_date + relativedelta(months=1)

        return True
