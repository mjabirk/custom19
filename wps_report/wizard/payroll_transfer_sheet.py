# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import time
import io
import zipfile
import logging
from odoo.exceptions import UserError
from collections import defaultdict

_logger = logging.getLogger(__name__)


class SalaryTransferSheet(models.TransientModel):
    """
    Salary Transfer Sheet
    Generates a ZIP file containing one or more SIF (Salary Information File)
    reports, grouped by the WPS Sponsor specified on the employee.
    """

    _name = "salary.transfer.sheet"
    _description = "Salary Transfer Sheet"

    # The 'bank_list' field is no longer needed here, as the bank format
    # is now determined by each employee's 'wps_sponsor_id' (res.partner).
    # Please remove 'bank_list' from this model and from the wizard's XML view.
    # bank_list = fields.Selection(...) # <-- REMOVE THIS

    export_file = fields.Binary(
        string='File',
        readonly=True
    )
    bank_list = fields.Selection([('hsb', 'HSBC Bank Middle East'), ('mar', 'Masraf Al Rayyan Bank'), ('qnb', 'Qatar National Bank'), ('cbq', 'Commercial Bank of Qatar')],string='Bank', required=True,default='qnb')

    export_filename = fields.Char(
        string='File Name',
        help="Name of the export file generated for this transfer sheet",
        store=True,  # Note: store=True on a transient model field is unusual, but kept from original
        readonly=True
    )

    def _generate_sif_for_group(self, sponsor, sponsor_bank_ac, slips, bank_format, payroll_reg):
        """
        Helper method to generate the SIF file content for a single group of payslips.
        Returns a tuple: (file_name, file_content_bytes)
        """
        data_lines = []

        # 1. Get Sponsor's Bank and Company Details
        bank_bic = sponsor_bank_ac.bank_id.bic or 'CONFIG_BIC'
        bank_acc_number = sponsor_bank_ac.acc_number.replace(" ", "") or 'CONFIG_ACC'

        # Use sponsor's details, not the company's
        employer_eid = sponsor.employer_eid or ''
        payer_eid = sponsor.payer_eid or ''
        payer_qid = sponsor.payer_qid or ''

        if not all([employer_eid, payer_eid, payer_qid, bank_bic != 'CONFIG_BIC', bank_acc_number != 'CONFIG_ACC']):
            _logger.warning(
                f"Skipping sponsor {sponsor.partner_id.name} due to incomplete WPS configuration (EID, QID, or Bank Details).")
            return None, None

        salary_month_str = payroll_reg.date_start.strftime('%Y%m')

        # 2. Generate Header Rows (Refactored)
        file_creation_date = time.strftime('%Y%m%d')
        file_creation_time = time.strftime('%H%M')

        header_cols_1 = [
            'Employer EID', 'File Creation Date', 'File Creation Time',
            'Payer EID', 'Payer QID', 'Payer Bank Short Name', 'Payer IBAN',
            'Salary Year and Month', 'Total Salaries', 'Total Records'
        ]
        header_data_1 = [
            employer_eid, file_creation_date, file_creation_time,
            payer_eid, payer_qid, bank_bic, bank_acc_number,
            salary_month_str, '__Total_Transfer__', '__Total_Records__'
        ]

        if bank_format in ('hsb', 'cbq'):
            header_cols_1.append('SIF Version')
            header_data_1.append('01')

        if bank_format == 'hsb':
            # Add HSBC specific additional header
            additional_header = sponsor.additional_header and time.strftime(sponsor.additional_header) or ''
            if additional_header:
                data_lines.append(additional_header)

        data_lines.append(','.join(header_cols_1))
        data_lines.append(','.join(header_data_1))

        # 3. Generate Data Column Header Row (Refactored)
        data_cols = [
            'Record Sequence', 'Employee QID', 'Employee Visa ID', 'Employee Name',
            'Employee Bank Short Name', 'Employee Account', 'Salary Frequency',
            'Number of Working days', 'Net Salary', 'Basic Salary', 'Extra hours',
            'Extra income', 'Deductions', 'Payment Type', 'Notes / Comments'
        ]
        if bank_format in ('hsb', 'cbq'):
            data_cols.extend([
                'Housing Allowance', 'Food Allowance', 'Transportation Allowance',
                'Overtime Allowance', 'Deduction Reason Code', 'Extra Field 1', 'Extra Field 2'
            ])

        data_lines.append(','.join(data_cols))

        # 4. Loop through Slips and Generate Data Rows
        total_rec = 0
        total_amount = 0
        for payslip in slips:
            if not payslip.employee_id.primary_bank_account_id:
                _logger.warning(
                    f"Skipping employee {payslip.employee_id.name} (in sponsor group {sponsor.partner_id.name}) due to missing bank account.")
                continue

            if not payslip.employee_id.identification_id:
                raise UserError(_(f"Please add QID/Identification No for employee {payslip.employee_id.name}."))

            total_rec += 1

            # --- Start of payslip line processing (same as original) ---
            overtime_hours = 0
            total_working_days = 0
            unpaid_leaves = False

            for worked_days_line in payslip.worked_days_line_ids:
                if worked_days_line.code in (
                'WORK100', 'Business', 'Leave_Reimbursement', 'Sick_Leave', 'Termination', 'Resignation'):
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

            net_salary = basic + allowance - deduction
            total_amount += round(net_salary)

            # This logic appears to be for calculating partial pay reasons
            # Keeping it as-is from the original
            contract_wage = payslip.version_id.wage  # Assuming 'version_id' is a custom field
            basic_diff = basic - contract_wage

            if deduction:
                Reason_Code = '04'
            if basic_diff < 0:
                Reason_Code = '01'  # Partial Pay
                deduction -= basic_diff  # Add the unpaid basic amount to deduction column
            else:
                allowance += basic_diff
            # --- End of payslip line processing ---

            emp_id = payslip.employee_id.identification_id.strip()
            emp_qid = emp_id if len(emp_id) == 11 else ''
            emp_visa_id = emp_id if len(emp_id) != 11 else ''

            emp_bank_bic = payslip.employee_id.primary_bank_account_id.bank_id.bic or ''
            emp_bank_acc = payslip.employee_id.primary_bank_account_id.acc_number.replace(" ", "") or ''

            data_line_items = [
                total_rec,
                emp_qid,
                emp_visa_id,
                payslip.employee_id.name,
                emp_bank_bic,
                emp_bank_acc,
                'M',  # Salary Frequency
                int(total_working_days),
                round(net_salary),
                round(contract_wage),
                overtime_hours,
                round(allowance),
                round(deduction),
                'Normal Payment' if bank_format == 'hsb' else '',
                (payslip.note or '').replace(',', ';')  # Ensure notes don't break CSV
            ]

            if bank_format in ('hsb', 'cbq'):
                data_line_items.extend([
                    Housing_Allowance,
                    Food_Allowance,
                    Transportation_Allowance,
                    Overtime_Allowance,
                    Reason_Code,
                    '',  # Extra Field 1
                    ''  # Extra Field 2
                ])

            data_lines.append(','.join(map(str, data_line_items)))

        if total_rec == 0:
            _logger.info(f"No valid payslips found for sponsor {sponsor.partner_id.name}. No file generated.")
            return None, None

        # 5. Finalize file content
        data = '\n'.join(data_lines)
        data = data.replace('__Total_Records__', str(total_rec))
        data = data.replace('__Total_Transfer__', str(total_amount))

        file_name = f'SIF_{payer_eid}_{bank_bic}_{file_creation_date}_{file_creation_time}.csv'

        return file_name, data.encode('utf-8')

    def generate_transfer_sheet(self, given_payroll_reg=False):
        """
        Main method to generate SIF files.
        Groups payslips by sponsor, generates a file for each,
        and returns a ZIP file.
        """
        if not given_payroll_reg:
            payroll_reg = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        else:
            payroll_reg = given_payroll_reg

        company = payroll_reg.company_id or self.env.company

        # Group payslips by sponsor
        # Employees without a sponsor will be grouped under the company's partner
        grouped_slips = defaultdict(list)
        for slip in payroll_reg.slip_ids:
            sponsor = slip.employee_id.wps_sponsor_id or company.partner_id.wps_sponsor_id
            grouped_slips[sponsor].append(slip)

        zip_buffer = io.BytesIO()
        files_generated = 0
        with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
            for sponsor, slips in grouped_slips.items():
                # Get the bank format from the sponsor partner
                # This requires the 'wps_bank_format' field on res.partner

                # Get the sponsor's bank account
                sponsor_bank_ac = sponsor.bank_account_id
                if not sponsor_bank_ac:
                    _logger.warning(
                        f"WPS SIF generation skipped for sponsor {sponsor.partner_id.name} (ID: {sponsor.id}) "
                        f"due to missing bank account on their partner record."
                    )
                    continue

                # Generate the file for this group
                file_name, file_content = self._generate_sif_for_group(
                    sponsor, sponsor_bank_ac, slips, self.bank_list, payroll_reg
                )

                if file_name and file_content:
                    zip_file.writestr(file_name, file_content)
                    files_generated += 1

        if files_generated == 0:
            raise UserError(
                _("No valid employee payslips or sponsor configurations found. No SIF files were generated."))

        # Get the zip file's content
        zip_b64 = base64.b64encode(zip_buffer.getvalue())
        zip_filename = f"WPS_SIF_Files_{payroll_reg.name.replace(' ', '_')}_{time.strftime('%Y%m%d')}.zip"

        if given_payroll_reg:
            # If called from another process, return the file data
            return (zip_filename, zip_b64)
        else:
            # If called from wizard, update self and return action
            self.export_file = zip_b64
            self.export_filename = zip_filename

            return {
                "view_mode": "form",
                "res_model": "salary.transfer.sheet",
                "res_id": self.id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": self.env.context,
                "nodestroy": True,
            }