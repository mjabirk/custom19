# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2016 Steigend IT Solutions
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################

from odoo import api, fields, models
from datetime import datetime, timedelta

class Partner(models.Model):
    _inherit = 'res.partner'

    partner_short_code = fields.Char('Short Code')