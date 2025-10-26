#-*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime, timedelta

class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'


    @api.model
    def _get_default_rule_ids(self):
        return [
            (0, 0, {
                'name': _('Basic Salary'),
                'sequence': 1,
                'code': 'BASIC',
                'category_id': self.env.ref('hr_payroll.BASIC').id,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': """Paid_Days = 0
if worked_days.get("WORK100"):
    Paid_Days += worked_days["WORK100"].number_of_days
if worked_days.get("PAIDLEAVE106"):
    Paid_Days += worked_days["PAIDLEAVE106"].number_of_days
if worked_days.get("LEAVE110"):
    Paid_Days += worked_days["LEAVE110"].number_of_days
if worked_days.get("Business"):
    Paid_Days += worked_days["Business"].number_of_days
if worked_days.get("Sick_Leave"):
    Paid_Days += worked_days["Sick_Leave"].number_of_days
if worked_days.get("Leave_Reimbursement"):
    Paid_Days += worked_days["Leave_Reimbursement"].number_of_days
if worked_days.get("Termination"):
    Paid_Days += worked_days["Termination"].number_of_days
if worked_days.get("Resignation"):
    Paid_Days += worked_days["Resignation"].number_of_days
if worked_days.get("Annual"):
    Paid_Days += worked_days["Annual"].number_of_days
	
month = payslip.date_from.month
year = payslip.date_from.year
if(month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12): tot_days = 31
elif((month == 2) and ((year%400==0) or (year%4==0 and year%100!=0))): tot_days = 29
elif(month == 2): tot_days = 28
else: tot_days = 30
	
result = round((tot_days ) and contract.wage*Paid_Days/(tot_days ) or 0)
            """,
            }),
            (0, 0, {
                'name': _('Accommodation Allowances'),
                'sequence': 20,
                'code': 'ACCO',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': 'result = contract.accommodation_allowance > 0',
                'amount_select': 'code',
                'amount_python_compute': """Paid_Days = 0
if worked_days.get("WORK100"):
    Paid_Days += worked_days["WORK100"].number_of_days
if worked_days.get("PAIDLEAVE106"):
    Paid_Days += worked_days["PAIDLEAVE106"].number_of_days
if worked_days.get("LEAVE110"):
    Paid_Days += worked_days["LEAVE110"].number_of_days
if worked_days.get("Business"):
    Paid_Days += worked_days["Business"].number_of_days
if worked_days.get("Sick_Leave"):
    Paid_Days += worked_days["Sick_Leave"].number_of_days
if worked_days.get("Leave_Reimbursement"):
    Paid_Days += worked_days["Leave_Reimbursement"].number_of_days
if worked_days.get("Termination"):
    Paid_Days += worked_days["Termination"].number_of_days
if worked_days.get("Resignation"):
    Paid_Days += worked_days["Resignation"].number_of_days
if worked_days.get("Annual"):
    Paid_Days += worked_days["Annual"].number_of_days
	
month = payslip.date_from.month
year = payslip.date_from.year
if(month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12): tot_days = 31
elif((month == 2) and ((year%400==0) or (year%4==0 and year%100!=0))): tot_days = 29
elif(month == 2): tot_days = 28
else: tot_days = 30
	
result =round((tot_days ) and contract.accommodation_allowance*Paid_Days/(tot_days ) or 0)
            """,
            }),
            (0, 0, {
                'name': _('Food Allowances'),
                'sequence': 25,
                'code': 'FOOD',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': 'result = contract.food_allowance > 0',
                'amount_select': 'code',
                'amount_python_compute': """Paid_Days = 0
if worked_days.get("WORK100"):
    Paid_Days += worked_days["WORK100"].number_of_days
if worked_days.get("PAIDLEAVE106"):
    Paid_Days += worked_days["PAIDLEAVE106"].number_of_days
if worked_days.get("LEAVE110"):
    Paid_Days += worked_days["LEAVE110"].number_of_days
if worked_days.get("Business"):
    Paid_Days += worked_days["Business"].number_of_days
if worked_days.get("Sick_Leave"):
    Paid_Days += worked_days["Sick_Leave"].number_of_days
if worked_days.get("Leave_Reimbursement"):
    Paid_Days += worked_days["Leave_Reimbursement"].number_of_days
if worked_days.get("Termination"):
    Paid_Days += worked_days["Termination"].number_of_days
if worked_days.get("Resignation"):
    Paid_Days += worked_days["Resignation"].number_of_days
	
month = payslip.date_from.month
year = payslip.date_from.year
if(month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12): tot_days = 31
elif((month == 2) and ((year%400==0) or (year%4==0 and year%100!=0))): tot_days = 29
elif(month == 2): tot_days = 28
else: tot_days = 30	
result = round( (tot_days ) and contract.food_allowance*Paid_Days/(tot_days ) or 0)
            """,
            }),
            (0, 0, {
                'name': _('Transportation Allowances'),
                'sequence': 30,
                'code': 'TRANS',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': 'result = contract.transportation_allowance > 0',
                'amount_select': 'code',
                'amount_python_compute': """
Paid_Days = 0
if worked_days.get("WORK100"):
    Paid_Days += worked_days["WORK100"].number_of_days
if worked_days.get("PAIDLEAVE106"):
    Paid_Days += worked_days["PAIDLEAVE106"].number_of_days
if worked_days.get("LEAVE110"):
    Paid_Days += worked_days["LEAVE110"].number_of_days
if worked_days.get("Business"):
    Paid_Days += worked_days["Business"].number_of_days
if worked_days.get("Sick_Leave"):
    Paid_Days += worked_days["Sick_Leave"].number_of_days
if worked_days.get("Leave_Reimbursement"):
    Paid_Days += worked_days["Leave_Reimbursement"].number_of_days
if worked_days.get("Termination"):
    Paid_Days += worked_days["Termination"].number_of_days
if worked_days.get("Resignation"):
    Paid_Days += worked_days["Resignation"].number_of_days
	
month = payslip.date_from.month
year = payslip.date_from.year
if(month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12): tot_days = 31
elif((month == 2) and ((year%400==0) or (year%4==0 and year%100!=0))): tot_days = 29
elif(month == 2): tot_days = 28
else: tot_days = 30	
result = round((tot_days ) and contract.transportation_allowance*Paid_Days/(tot_days ) or 0)
            """,
            }),
            (0, 0, {
                'name': _('Other Allowances'),
                'sequence': 35,
                'code': 'OTHER',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': 'result = contract.other_allowance > 0',
                'amount_select': 'code',
                'amount_python_compute': """Paid_Days = 0
if worked_days.get("WORK100"):
    Paid_Days += worked_days["WORK100"].number_of_days
if worked_days.get("PAIDLEAVE106"):
    Paid_Days += worked_days["PAIDLEAVE106"].number_of_days
if worked_days.get("LEAVE110"):
    Paid_Days += worked_days["LEAVE110"].number_of_days
if worked_days.get("Business"):
    Paid_Days += worked_days["Business"].number_of_days
if worked_days.get("Sick_Leave"):
    Paid_Days += worked_days["Sick_Leave"].number_of_days
if worked_days.get("Leave_Reimbursement"):
    Paid_Days += worked_days["Leave_Reimbursement"].number_of_days
if worked_days.get("Termination"):
    Paid_Days += worked_days["Termination"].number_of_days
if worked_days.get("Resignation"):
    Paid_Days += worked_days["Resignation"].number_of_days
	
month = payslip.date_from.month
year = payslip.date_from.year
if(month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12): tot_days = 31
elif((month == 2) and ((year%400==0) or (year%4==0 and year%100!=0))): tot_days = 29
elif(month == 2): tot_days = 28
else: tot_days = 30	
result = round((tot_days ) and contract.other_allowance*Paid_Days/(tot_days ) or 0)
            """,
            }),
            (0, 0, {
                'name': _('Overtime Hours'),
                'sequence': 40,
                'code': 'OT',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': 'result =worked_days.OT and worked_days.OT.number_of_hours',
                'amount_select': 'code',
                'amount_python_compute': """DAYS_PER_MONTH = 365.0 / 12
WORKING_TIME = 8
rate = contract.wage / DAYS_PER_MONTH / WORKING_TIME
overtime_line_ids = employee.overtime_line_ids.search([('employee_id','=',employee.id) ,('date_from', '>=', payslip.date_from), ('date_from', '<=', payslip.date_to),('type','=','overtime'), ('state','=','approved'),])
tot_hours = 0
for ot in overtime_line_ids :
    tot_hours  += ot.duration
result = round((worked_days.get("OT") and worked_days["OT"].number_of_hours*rate or 0) + (inputs.get("OT") and inputs["OT"].amount or 0) + tot_hours *rate )""",
            }),
            (0, 0, {
                'name': _('Bonus'),
                'sequence': 45,
                'code': 'OTA',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': """overtime_line_ids = employee.overtime_line_ids.search([('employee_id','=',employee.id),('date_from', '>=', payslip.date_from), ('date_from', '<=', payslip.date_to),('type','=','bonus'),('state','=','approved'),])
tot_amount  = 0
for ot in overtime_line_ids :
    tot_amount  += ot.ot_amount
result = round(tot_amount)""",
                'amount_select': 'code',
                'amount_python_compute': """overtime_line_ids = employee.overtime_line_ids.search([('employee_id','=',employee.id),('date_from', '>=', payslip.date_from), ('date_from', '<=', payslip.date_to),('type','=','bonus'),('state','=','approved'),])
tot_amount  = 0
for ot in overtime_line_ids :
    tot_amount  += ot.ot_amount
result = round(tot_amount)""",
            }),
            (0, 0, {
                'name': _('Air Ticket'),
                'sequence': 50,
                'code': 'AIRTKT',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': """leaves_available=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','<=',payslip.date_to),('request_date_from','>=',payslip.date_from),('holiday_status_id.name','in',['Eligible_Leave', 'Resignation', 'Termination']),('air_ticket','>',0)])
if leaves_available:
    result = True
else:
  if not result:
    year = payslip.date_to .year
    month = payslip.date_to .month
    day = payslip.date_to .day
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_month[1] = 29
    if day < days_in_month[month - 1]:
        next_day = date(year, month, day + 1)
    else:
        if month == 12:
            next_day = date(year + 1, 1, 1)
        else:
            next_day = date(year, month + 1, 1)
    annual_leave_pay=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','<=',next_day ),('request_date_from','>',payslip.date_from),('holiday_status_id.name','in',['Resignation',     'Annual Leave', 'Termination'])],order='request_date_from desc', limit = 1)
    if annual_leave_pay.air_ticket:
        result = True
    else:
       result = False""",
                'amount_select': 'code',
                'amount_python_compute': """result = 0
if  (worked_days.get("Resignation") or worked_days.get("Termination")) :
    result +=round( contract.air_ticket)
    #if contract.structure_type_id.name in ('Employee', 'Administration'):
    #    result +=round( contract.air_ticket)
    #else:
    #    result += round(contract.air_ticket*.75)
leaves_available=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','<=',payslip.date_to),('request_date_from','>=',payslip.date_from),('holiday_status_id.name','in',['Eligible_Leave', 'Resignation', 'Termination']),('air_ticket','>',0)])
for leave in leaves_available:
    if leave.air_ticket:
        result = leave.air_ticket
if not result:
    year = payslip.date_to .year
    month = payslip.date_to .month
    day = payslip.date_to .day
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
        days_in_month[1] = 29
    if day < days_in_month[month - 1]:
        next_day = date(year, month, day + 1)
    else:
        if month == 12:
            next_day = date(year + 1, 1, 1)
        else:
            next_day = date(year, month + 1, 1)
    annual_leave_pay=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','<=',next_day ),('request_date_from','>',payslip.date_from),('holiday_status_id.name','in',['Resignation',     'Annual Leave', 'Termination'])],order='request_date_from desc', limit = 1)
    result =annual_leave_pay.air_ticket""",
            }),
            (0, 0, {
                'name': _('Leave Pay'),
                'sequence': 55,
                'code': 'LP',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': """year = payslip.date_to .year
month = payslip.date_to .month
day = payslip.date_to .day
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
    days_in_month[1] = 29
if day < days_in_month[month - 1]:
    next_day = date(year, month, day + 1)
else:
    if month == 12:
        next_day = date(year + 1, 1, 1)
    else:
        next_day = date(year, month + 1, 1)
annual_leave_pay=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','<=',next_day ),('request_date_from','>',payslip.date_from),('holiday_status_id.name','in',['Resignation', 'Annual Leave', 'Termination'])],order='request_date_from desc', limit = 1)
result =worked_days.get("Termination") or worked_days.get("Resignation") or annual_leave_pay""",
                'amount_select': 'code',
                'amount_python_compute': """
date_from = contract.date_start
annual_leave=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','<',payslip.date_from),('request_date_from','>=',date_from),('holiday_status_id.name','in',['Resignation', 'Annual Leave', 'Termination'])],order='request_date_from desc', limit = 1)
if annual_leave:
    date_from = annual_leave.request_date_to
date_to = payslip.date_to
leaves=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','<=',payslip.date_to),('request_date_from','>=',payslip.date_from),('holiday_status_id.name','in',['Termination','Resignation','Annual Leave'])])
if leaves:
    date_to  = leaves[0].request_date_from
unpaid_leaves=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','>=',date_from),('request_date_from','<=',date_to),('holiday_status_id.name','in',['Unpaid','Absent'])])
unpaid_days=0
for unpaid_leave in unpaid_leaves:
    unpaid_days += unpaid_leave.number_of_days
delay = (date_to - date_from ).days - unpaid_days  +1
result = round((contract.leave_pay_days * (delay / 365)) * contract.wage*12/365) or 0
result_name = 'Leave pay ({} days ) - بدل اجازة'.format(delay )""",
            }),
            (0, 0, {
                'name': _('End of Service'),
                'sequence': 65,
                'code': 'EOS',
                'category_id': self.env.ref('hr_payroll.ALW').id,
                'condition_select': 'python',
                'condition_python': 'result = worked_days.Termination  or  worked_days.Resignation ',
                'amount_select': 'code',
                'amount_python_compute': """date_from = contract.date_start
date_to = payslip.date_from
leaves=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','<=',payslip.date_to),('request_date_from','>=',payslip.date_from),('holiday_status_id.name','in',['Termination','Resignation'])])
if leaves:
    date_to  = leaves[0].request_date_from
delay = (date_to  -date_from ).days

delay = (date_to  -date_from ).days+1

unpaid_leaves=employee.leave_ids.search([('employee_id','=',employee.id),('state','=','validate'),('request_date_from','>=',date_from),('request_date_from','<=',payslip.date_from),('holiday_status_id.name','in',['Unpaid','Absent'])])
unpaid_days=0
for unpaid_leave in unpaid_leaves:
    unpaid_days += unpaid_leave.number_of_days
if unpaid_days > 15:
    unpaid_days -= 15
else:
    unpaid_days = 0
if delay <= unpaid_days:
    delay = 0
else:
    delay = delay - unpaid_days
result = round((contract.wage  * contract.eos_days * 12 * delay / (365 * 365)) or 0)""",
            }),
            (0, 0, {
                'name': _('Leave Pay Accrual'),
                'sequence': 150,
                'code': 'LPAC',
                'category_id': self.env.ref('hr_payroll.COMP').id,
                'condition_select': 'none',
                'amount_select': 'code',
                'appears_on_payslip':False,
                'amount_python_compute': """
Paid_Days = 0
if worked_days.get("WORK100"):
    Paid_Days += worked_days["WORK100"].number_of_days
if worked_days.get("PAIDLEAVE106"):
    Paid_Days += worked_days["PAIDLEAVE106"].number_of_days
if worked_days.get("LEAVE110"):
    Paid_Days += worked_days["LEAVE110"].number_of_days
if worked_days.get("Business"):
    Paid_Days += worked_days["Business"].number_of_days
if worked_days.get("Sick_Leave"):
    Paid_Days += worked_days["Sick_Leave"].number_of_days
if worked_days.get("Leave_Reimbursement"):
    Paid_Days += worked_days["Leave_Reimbursement"].number_of_days
if worked_days.get("Termination"):
    Paid_Days += worked_days["Termination"].number_of_days
if worked_days.get("Resignation"):
    Paid_Days += worked_days["Resignation"].number_of_days
	
month = payslip.date_from.month
year = payslip.date_from.year
if(month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12): tot_days = 31
elif((month == 2) and ((year%400==0) or (year%4==0 and year%100!=0))): tot_days = 29
elif(month == 2): tot_days = 28
else: tot_days = 30	
result = tot_days and round((contract.wage+ contract.accommodation_allowance)*contract.leave_pay_days*Paid_Days /(365*(365/12))) or 0""",
            }),
            (0, 0, {
                'name': _('End of Service Accrual'),
                'sequence': 155,
                'code': 'EOSAC',
                'category_id': self.env.ref('hr_payroll.COMP').id,
                'condition_select': 'none',
                'appears_on_payslip':False,
                'amount_select': 'code',
                'amount_python_compute': """Paid_Days = 0
if worked_days.get("WORK100"):
    Paid_Days += worked_days["WORK100"].number_of_days
if worked_days.get("PAIDLEAVE106"):
    Paid_Days += worked_days["PAIDLEAVE106"].number_of_days
if worked_days.get("LEAVE110"):
    Paid_Days += worked_days["LEAVE110"].number_of_days
if worked_days.get("Business"):
    Paid_Days += worked_days["Business"].number_of_days
if worked_days.get("Sick_Leave"):
    Paid_Days += worked_days["Sick_Leave"].number_of_days
if worked_days.get("Leave_Reimbursement"):
    Paid_Days += worked_days["Leave_Reimbursement"].number_of_days
if worked_days.get("Termination"):
    Paid_Days += worked_days["Termination"].number_of_days
if worked_days.get("Resignation"):
    Paid_Days += worked_days["Resignation"].number_of_days
if worked_days.get("Annual"):
    Paid_Days += worked_days["Annual"].number_of_days
if worked_days.get("Unpaid"):
    Paid_Days += worked_days["Unpaid"].number_of_days

month = payslip.date_from.month
year = payslip.date_from.year
if(month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12): tot_days = 31
elif((month == 2) and ((year%400==0) or (year%4==0 and year%100!=0))): tot_days = 29
elif(month == 2): tot_days = 28
else: tot_days = 30
result = tot_days  and round(contract.wage * contract.eos_days * Paid_Days / (365 * (365/12))) or 0       """,
            }),
            (0, 0, {
                'name': _('Deduction'),
                'sequence': 180,
                'code': 'DEDUCTION',
                'category_id': self.env.ref('hr_payroll.DED').id,
                'condition_select': 'python',
                'condition_python': """result = len(employee.overtime_line_ids.search([('employee_id','=',employee.id),('date_from', '>=', payslip.date_from), ('date_from', '<=', payslip.date_to),('type','=','deduction'),('state','=','approved'), ('ot_amount','<',0)])) or inputs.get("DED")""",
                'amount_select': 'code',
                'amount_python_compute': """result = 0
overtime_line_ids = employee.overtime_line_ids.search([('employee_id','=',employee.id),('date_from', '>=', payslip.date_from), ('date_from', '<=', payslip.date_to),('type','=','deduction'),('state','=','approved'), ('ot_amount','<',0)]) 
reason=''
for ot in overtime_line_ids :
    result  += -1*ot.ot_amount
    reason += f'{ot.name}: {ot.amount} {payslip.currency_id.symbol}. '
result = round(result)
result_name  = reason 
if  inputs.get("DED"):
    result += inputs["DED"].amount
    result_name  += inputs["DED"].name""",
            }),
            (0, 0, {
                'name': _('Net Salary'),
                'sequence': 200,
                'code': 'NET',
                'category_id': self.env.ref('hr_payroll.NET').id,
                'condition_select': 'none',
                'amount_select': 'code',
                'amount_python_compute': 'result = categories["BASIC"] + categories["ALW"] - categories["DED"]',
            })
        ]

    rule_ids = fields.One2many(
        'hr.salary.rule', 'struct_id',
        string='Salary Rules', default=_get_default_rule_ids)


    def _generate_sheet(self):
        last_day_of_previous_month = datetime.today().replace(day=1) - timedelta(days=1)
        first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
