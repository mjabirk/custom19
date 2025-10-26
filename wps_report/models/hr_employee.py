# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    leave_ids = fields.One2many('hr.leave', 'employee_id')
    joining_date = fields.Date(string='Joining Date')
    wps_sponsor_id = fields.Many2one(
        'hr.wps.sponsor',
        string="WPS Sponsor",
        ondelete='restrict',  # Prevents deleting a sponsor if employees are linked
        tracking=True,
        help="Sponsor responsible for the employee's WPS salary transfer."
    )

# class HrEmployeePublic(models.Model):
#     _inherit = "hr.employee.public"
#     _description = "Employee Category"
#
#     joining_date = fields.Date(string='Joining Date')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: