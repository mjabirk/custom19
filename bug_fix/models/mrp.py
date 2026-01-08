# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mobile = fields.Char(
        "Mobile")
    #
    # @api.depends('procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id')
    # def _get_mobile_no(self):
    #     for production in self:
    #         sales = production.procurement_group_id.mrp_production_ids.move_dest_ids.group_id.sale_id
    #         production.mobile = sales.partner_shipping_id.mobile or sales.partner_shipping_id.phone
    #
    #
    # def _sms_get_number_fields(self):
    #     """ This method returns the fields to use to find the number to use to
    #     send an SMS on a record. """
    #     return ['mobile']
    #
