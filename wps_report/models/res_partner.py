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

    employer_eid = fields.Char('Employer EID.', size=8)
    payer_eid = fields.Char(' Payer EID.', size=8)
    payer_qid = fields.Char('Payer QID.', size=11)
    additional_header = fields.Char('Additional Header', size=64,help='Additional Header for HSBC Bank. Add entires in coma seperated format. Eg:QAWPS,ABC19361001,P,R%m%M,%y%m%d,W01')