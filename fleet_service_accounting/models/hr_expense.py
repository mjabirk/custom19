# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'hr.expense'

    fleet_service_id = fields.Many2one('fleet.vehicle.log.services', string="Fleet Service", readonly=False)
    fleet_service_line_id = fields.Many2one('fleet.service.products', string="Fleet Service Lines", readonly=False)
