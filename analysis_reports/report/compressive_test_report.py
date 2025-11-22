# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _


class CompressiveTestReport(models.AbstractModel):
    _name = 'report.analysis_reports.compressive_test_report'
    _description = 'Compressive Test Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': docs,
        }
