# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    guarantee_check = fields.Boolean(string="Guarantee check", default=False)
