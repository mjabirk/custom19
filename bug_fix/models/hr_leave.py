# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def unlink(self):
        work_entries = self.env['hr.work.entry'].sudo().search([('leave_id', 'in', self.ids)])
        work_entries.write({'active': False})
        ret = super().unlink()
        vals_list = []
        for work_entry in work_entries:
            vals_list += work_entry.contract_id._get_work_entries_values(work_entry.date_start, work_entry.date_stop)
        self.env['hr.work.entry'].create(vals_list)
        return ret