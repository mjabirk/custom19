# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    def copy(self, default=None):
        default = dict(default or {})
        if self.partner_id.sale_warn == 'block':
            default['partner_id'] = None
            default['partner_invoice_id'] = None
            default['partner_shipping_id'] = None
            default['pricelist_id'] = None

        return super().copy(default)


    mobile = fields.Char(related='partner_id.phone')


    def _sms_get_number_fields(self):
        """ This method returns the fields to use to find the number to use to
        send an SMS on a record. """
        return ['mobile', 'phone']