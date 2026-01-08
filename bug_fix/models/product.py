# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.onchange('property_valuation')
    def onchange_property_valuation(self):
        if not self._origin:
            # don't display the warning when creating a product category
            return
        return {
            'warning': {
                'title': _("Warning"),
                'message': _("Changing the Inventory Valuation method will impact how accounting entries are recorded during stock movements. To ensure the accuracy of inventory accounting based on actual stock, it's important to keep it automated. Switching to manual valuation can significantly affect accounting, potentially causing errors in the balance sheet."),
            }
        }