# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    maintenance_request_id = fields.Many2one('maintenance.request', string="Maintenance Request", readonly=False)
    maintenance_request_lines_id = fields.Many2one('maintenance.request.lines', string="Maintenance Request Lines", readonly=False)
