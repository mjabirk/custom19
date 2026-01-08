# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"
    maintenance_request_lines_id = fields.Many2one('maintenance.request.lines', string="Maintenance Request Lines", readonly=False)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    maintenance_request_id = fields.Many2one('maintenance.request', string="Maintenance Request", readonly=False)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    maintenance_request_id = fields.Many2one('maintenance.request', string="Maintenance Request", readonly=False)


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    maintenance_request_lines_id = fields.Many2one('maintenance.request.lines', string="Maintenance Request Lines", readonly=False)
