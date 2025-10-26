# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import time
from odoo.exceptions import UserError

class SalaryTransferSheet(models.TransientModel):
    """Salary Transfer Sheet"""

    _name = "salary.transfer.sheet"
    _description = "Salary Transfer Sheet"
    def blank_file(self):
        return  'Blank.txt'
    bank_list = fields.Selection([('hsb', 'HSBC Bank Middle East'), ('mar', 'Masraf Al Rayyan Bank'), ('qnb', 'Qatar National Bank'), ('cbq', 'Commercial Bank of Qatar')],string='Bank', required=True,default='qnb')
    export_file = fields.Binary(string='File',readonly=True)
    export_filename = fields.Char(string='File Name', help="Name of the export file generated for this transfer sheet", store=True,readonly=True)
    def generate_transfer_sheet(self, given_payroll_reg=False, wps_bank=False):
        #self.ensure_one()
        if not given_payroll_reg:
            payroll_reg = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        else:
            payroll_reg = given_payroll_reg
        company = payroll_reg.company_id or self.env.company
        data_lines = []
        bank_bic = company.partner_id.bank_ids and company.partner_id.bank_ids[0].bank_id.bic or 'Configure Bank in Company Partner'
        bank_acc_number=company.partner_id.bank_ids and company.partner_id.bank_ids[0].acc_number.replace(" ", "") or 'Configure Bank in Company Partner'
        bank = wps_bank or self.bank_list
        if bank == 'hsb':
            additional_header = company.partner_id.additional_header and time.strftime(company.partner_id.additional_header) or ''
            data_lines.append(additional_header)
            data_lines.append('Employer EID,File Creation Date,File Creation Time,Payer EID,Payer QID,Payer Bank Short Name,Payer IBAN,Salary Year and Month,Total salaries,Total records,SIF Version')
            data_lines.append('%s,%s,%s,%s,%s,%s,%s,%s,__Total_Transfer__,__Total_Records__,01' % (company.partner_id.employer_eid or '',
                                                                                time.strftime('%Y%m%d'),
                                                                                time.strftime('%H%M'),
                                                                                company.partner_id.payer_eid or '',
                                                                                company.partner_id.payer_qid or '',
                                                                                bank_bic,
                                                                                bank_acc_number,
                                                                                payroll_reg.date_start.strftime('%Y%m')))
        elif bank in ('cbq',):
            data_lines.append('Employer EID,File Creation Date,File Creation Time,Payer EID,Payer QID,Payer Bank Short Name,Payer IBAN,Salary Year and Month,Total Salaries,Total Records,SIF Version')
            data_lines.append(
                '%s,%s,%s,%s,%s,%s,%s,%s,__Total_Transfer__,__Total_Records__,01' % (company.partner_id.employer_eid or '',
                                                                                  time.strftime('%Y%m%d'),
                                                                                  time.strftime('%H%M'),
                                                                                  company.partner_id.payer_eid or '',
                                                                                  company.partner_id.payer_qid or '',
                                                                                  bank_bic,
                                                                                  bank_acc_number,
                                                                                  payroll_reg.date_start.strftime('%Y%m')))
        elif bank in ('mar','qnb'):
            data_lines.append('Employer EID,File Creation Date,File Creation Time,Payer EID,Payer QID,Payer Bank Short Name,Payer IBAN,Salary Year and Month,Total Salaries,Total Records')
            data_lines.append(
                '%s,%s,%s,%s,%s,%s,%s,%s,__Total_Transfer__,__Total_Records__' % (company.partner_id.employer_eid or '',
                                                                                  time.strftime('%Y%m%d'),
                                                                                  time.strftime('%H%M'),
                                                                                  company.partner_id.payer_eid or '',
                                                                                  company.partner_id.payer_qid or '',
                                                                                  bank_bic,
                                                                                  bank_acc_number,
                                                                                  payroll_reg.date_start.strftime('%Y%m')))
        if bank == 'hsb':
            data_lines.append('Record Id,Employee QID,Employee Visa ID,Employee Name,Employee Bank Short Name,Employee Account #,Salary Frequency,Number of working Days,Net Salary,Basic Salary,Extra hours,Extra Income,Deductions,Payment Type,Notes / Comments,Housing Allowance,Food Allowance,Transportation Allowance,Overtime Allowance,Deduction Reason Code,Extra Field 1,Extra Field 2')
        elif bank in ('cbq',):
            data_lines.append('Record Sequence,Employee QID,Employee Visa ID,Employee Name,Employee Bank Short Name,Employee Account,Salary Frequency,Number of Working days,Net Salary,Basic Salary,Extra hours,Extra income,Deductions,Payment Type,Notes / Comments,Housing Allowance,Food Allowance,Transportation Allowance,Overtime Allowance,Deduction Reason Code,Extra Field 1,Extra Field 2')
        elif bank in ('mar','qnb'):
            data_lines.append('Record Sequence,Employee QID,Employee Visa ID,Employee Name,Employee Bank Short Name,Employee Account,Salary Frequency,Number of Working days,Net Salary,Basic Salary,Extra hours,Extra income,Deductions,Payment Type,Notes / Comments')

        total_rec = 0
        total_amount=0
        for payslip in payroll_reg.slip_ids:
            if payslip.employee_id.bank_account_id:
                if not payslip.employee_id.identification_id:
                    raise UserError(_("Please add Identification No for employee {}.".format(payslip.employee_id.name)))

                total_rec += 1
                overtime_hours = 0
                total_working_days = 0
                unpaid_leaves = False

                for worked_days_line in payslip.worked_days_line_ids:
                    if worked_days_line.code in ('WORK100','Business','Leave_Reimbursement','Sick_Leave','Termination','Resignation'):
                        total_working_days += worked_days_line.number_of_days
                    else:
                        unpaid_leaves = True
                basic = 0
                allowance = 0
                deduction = 0
                Housing_Allowance = 0
                Food_Allowance = 0
                Transportation_Allowance = 0
                Overtime_Allowance = 0
                Deduction = 0
                Reason_Code = ''
                for line in payslip.line_ids:
                    if line.category_id.code == 'BASIC':
                        basic += line.total
                    elif line.category_id.code == 'ALW':
                        allowance += line.total
                    elif line.category_id.code == 'DED':
                        deduction += line.total
                    elif line.code == 'LOAN':
                        deduction += line.total
                    if line.code == 'ACCO':
                        Housing_Allowance += line.total
                    elif line.code == 'FOOD':
                        Food_Allowance += line.total
                    elif line.code == 'TRANS':
                        Transportation_Allowance += line.total
                    elif line.code == 'OT':
                        Overtime_Allowance += line.total
                total_amount += round(basic+allowance-deduction)
                net_salary = basic+allowance-deduction
                basic_diff = basic-payslip.contract_id.wage
                if deduction:
                    Reason_Code = '04'
                if basic_diff <0:
                    Reason_Code = '01'
                    deduction -= basic_diff
                else:
                    allowance += basic_diff
                data_line = '%s,%s,%s,%s,%s,%s,M,%s,%s,%s,%s,%s,%s,%s,%s' %(total_rec,
                                   len(payslip.employee_id.identification_id.strip()) == 11 and payslip.employee_id.identification_id or '',
                                   len(payslip.employee_id.identification_id.strip()) != 11 and payslip.employee_id.identification_id or '',
                                   payslip.employee_id.name,
                                   payslip.employee_id.bank_account_id.bank_id.bic or '',
                                   payslip.employee_id.bank_account_id.acc_number.replace(" ", "") or '',
                                   int(total_working_days),
                                   round(net_salary),
                                   round(payslip.contract_id.wage),
                                   overtime_hours,
                                   round(allowance),
                                   round(deduction),
                                   self.bank_list == 'hsb' and 'Normal Payment' or '',
                                   (payslip.note or '')
                                   )
                if self.bank_list in ('hsb','cbq'):
                    data_line += ',%s,%s,%s,%s,%s,,'%(Housing_Allowance,Food_Allowance,Transportation_Allowance,Overtime_Allowance,Reason_Code)
                data_lines.append(data_line)
        data = '\n'.join(data_lines)
        data = data.replace('__Total_Records__', str(total_rec))
        data = data.replace('__Total_Transfer__', str(total_amount))
        file_data = base64.encodebytes(data.encode())
        file_name = 'SIF_%s_%s_%s_%s.csv' % (company.partner_id.payer_eid, bank_bic, time.strftime('%Y%m%d'), time.strftime('%H%M'))
        if given_payroll_reg:
            return (file_name,file_data)
        else:
            self.export_file = file_data
            self.export_filename = file_name
            return {
                "view_mode": "form",
                "res_model": "salary.transfer.sheet",
                "res_id": self.id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": self.env.context,
                "nodestroy": True,
            }