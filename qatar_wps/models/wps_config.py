# -*- coding: utf-8 -*-
from odoo import models, fields

class HrWpsConfig(models.Model):
    _name = 'hr.wps.config'
    _description = 'Qatar WPS Configuration'

    name = fields.Char(string='Name', required=True, help='e.g., Main Company WPS')
    wps_employer_id = fields.Char(string='Employer ID (Establishment ID)', required=True, help='Company Registration Card Number / Establishment ID')
    wps_bank_short_name = fields.Char(string='Bank Short Name', required=True, help='Payer Bank Short Name (e.g., QNB, CBQ)')
    wps_payer_iban = fields.Char(string='Payer IBAN', required=True, help='International Bank Account Number of the Payer')
    wps_payer_id = fields.Char(string='Payer ID', required=True, help='Payer Establishment ID or QID')
