# -*- coding: utf-8 -*-
import base64
import csv
import io
import zipfile
from datetime import datetime
from odoo import models, fields, _
from odoo.exceptions import UserError

class QatarWpsWizard(models.TransientModel):
    _name = 'qatar.wps.wizard'
    _description = 'Qatar WPS Wizard'

    batch_ids = fields.Many2many('hr.payslip.run', string='Payslip Batches')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    
    # Binary fields for download
    sif_file = fields.Binary('SIF File', readonly=True)
    sif_filename = fields.Char('Filename', readonly=True)

    def generate_wps_file(self):
        self.ensure_one()
        
        # 1. Fetch Payslips
        domain = [('state', '=', 'done')]
        if self.batch_ids:
            domain.append(('payslip_run_id', 'in', self.batch_ids.ids))
        elif self.date_start and self.date_end:
            domain.append(('date_from', '>=', self.date_start))
            domain.append(('date_to', '<=', self.date_end))
        else:
            raise UserError(_("Please select Payslip Batches or a Date Range."))

        payslips = self.env['hr.payslip'].search(domain)
        
        if not payslips:
            raise UserError(_("No payslips found for the selected criteria."))

        # 2. Group by WPS Config
        grouped_payslips = {}
        no_config_employees = []
        
        for slip in payslips:
            config = slip.employee_id.wps_config_id
            if not config:
                no_config_employees.append(slip.employee_id.name)
                continue
            
            if config not in grouped_payslips:
                grouped_payslips[config] = self.env['hr.payslip']
            grouped_payslips[config] |= slip

        if no_config_employees:
            # Optionally raise error or skip. Raising error is safer to ensure compliance.
            raise UserError(_("The following employees do not have a WPS Configuration assigned:\n%s") % ", ".join(set(no_config_employees)))

        if not grouped_payslips:
             raise UserError(_("No valid WPS Configuration found for the selected payslips."))

        # 3. Generate Content
        generated_files = [] # List of (filename, data_bytes)

        for config, slips in grouped_payslips.items():
            csv_data, filename = self._generate_sif_content(config, slips)
            generated_files.append((filename, csv_data))

        # 4. Return Single File or Zip
        if len(generated_files) == 1:
            filename, data = generated_files[0]
            self.sif_file = base64.b64encode(data)
            self.sif_filename = filename
        else:
            # Create Zip
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
                for fname, fcontent in generated_files:
                    zf.writestr(fname, fcontent)
            
            self.sif_file = base64.b64encode(zip_buffer.getvalue())
            self.sif_filename = "WPS_Batch_Export_%s.zip" % fields.Date.today().strftime('%Y%m%d')

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'qatar.wps.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def _generate_sif_content(self, config, payslips):
        """ Helper to generate SIF CSV content for a specific config and set of payslips """
        employer_id = config.wps_employer_id
        payer_bank = config.wps_bank_short_name
        payer_id = config.wps_payer_id
        payer_iban = config.wps_payer_iban
        
        creation_date = fields.Date.today().strftime('%Y%m%d')
        creation_time = datetime.now().strftime('%H%M')
        
        # Calculate totals
        total_salaries = sum(payslips.mapped('net_wage'))
        record_count = len(payslips)
        
        # Salary Year/Month
        # Use the earliest start date from payslips or wizard date
        if self.date_start:
             ref_date = self.date_start
        elif payslips:
             # Try to take from first payslip or batch
             ref_date = payslips[0].date_from
        else:
             ref_date = fields.Date.today() # Fallback

        salary_year_month = ref_date.strftime('%Y%m')

        output = io.StringIO()
        writer = csv.writer(output)

        # Header Row 1
        writer.writerow(['Employer ID', 'Creation Date', 'Creation Time', 'Payer ID', 'Payer Bank', 'Payer IBAN', 'Salary YearMonth', 'Total Salaries', 'Records', 'Version'])
        
        # Header Row 2
        writer.writerow([
            employer_id, 
            creation_date, 
            creation_time, 
            payer_id, 
            payer_bank, 
            payer_iban,
            salary_year_month, 
            "{:.2f}".format(total_salaries), 
            record_count, 
            '01'
        ])
        
        # Row 3
        writer.writerow(['Record S.N.', 'Employee QID', 'Employee Name', 'Employee Bank', 'Employee Account', 'Net Salary', 'Basic Salary', 'Salary Freq', 'Deductions', 'Payment Type', 'Notes']) 
        
        # Row 4+
        serial = 1
        for slip in payslips:
            emp = slip.employee_id
            qid = emp.identification_id or ''
            name = emp.name
            bank_short = emp.bank_account_id.bank_id.bic or ''
            emp_iban = emp.bank_account_id.acc_number or ''
            net = slip.net_wage
            basic = slip.contract_id.wage # or basic category
            
            freq = 'M'
            if slip.contract_id.schedule_pay == 'bi-weekly':
                freq = 'B'
            elif slip.contract_id.schedule_pay == 'weekly':
                freq = 'W'
                
            writer.writerow([
                serial,
                qid,
                name,
                bank_short,
                emp_iban,
                "{:.2f}".format(net),
                "{:.2f}".format(basic),
                freq,
                0,
                'Salary',
                ''
            ])
            serial += 1
            
        return output.getvalue().encode('utf-8'), f"SIF_{employer_id}_{payer_bank}_{creation_date}_{creation_time}.csv"
