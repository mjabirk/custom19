# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Steigend IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import api, fields, models

class Partner(models.Model):
    _inherit = 'res.partner'
    wps_sponsor_id = fields.Many2one(
        'hr.wps.sponsor',
        string="WPS Sponsor",
        ondelete='restrict',  # Prevents deleting a sponsor if partners are linked
        tracking=True,
        help="Sponsor responsible for the employee's WPS salary transfer."
    )
