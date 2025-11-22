# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from odoo import api, fields, models, _


class MixDesignReport(models.AbstractModel):
    _name = 'report.analysis_reports.mix_design_report'
    _description = 'Mix Design Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.bom'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'mrp.bom',
            'docs': docs,
        }
