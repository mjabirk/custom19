# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"
    fleet_service_line_id = fields.Many2one('fleet.service.products', 'Service Product Line', index=True,readonly=False)

class Partner(models.Model):
    _inherit = 'res.partner'
    mobile_number = fields.Char('Mobile Number')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    fleet_service_id = fields.Many2one('fleet.vehicle.log.services', string="Fleet Service", readonly=False)
    mobile = fields.Char(related='partner_id.mobile_number')


    def _sms_get_number_fields(self):
        """ This method returns the fields to use to find the number to use to
        send an SMS on a record. """
        return ['mobile']

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    fleet_service_id = fields.Many2one('fleet.vehicle.log.services', string="Fleet Service", readonly=False)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    fleet_service_line_id = fields.Many2one('fleet.service.products', 'Service Product Line', index=True,readonly=False)