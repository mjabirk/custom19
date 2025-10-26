# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    leave_ids = fields.One2many('hr.leave', 'employee_id')

    joining_date = fields.Date(string='Joining Date')

class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"
    _description = "Employee Category"

    joining_date = fields.Date(string='Joining Date')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: