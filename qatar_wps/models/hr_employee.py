# -*- coding: utf-8 -*-
from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    wps_config_id = fields.Many2one('hr.wps.config', string='WPS Employer', help='Select the WPS Configuration (Employer) for this employee.')
