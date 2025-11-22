# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    absorption_pc = fields.Float('Absorption %', default=0.0, digits='Quality Tests')
    spec_gravity = fields.Float('Spec. Gravity', default=0.0, digits='Quality Tests')

class MrpBom(models.Model):
    _inherit = 'mrp.bom'
    strength_grade = fields.Char('Strength Grade', default='Cube 35 Mpa @ 28 days')
    max_agg_size = fields.Integer('Max. Size of Aggregates')
    tot_cem_mat= fields.Integer('Total Cementitious Materials, kg / m³')
    min_cem_con = fields.Integer('Min. Cement Content (QCS 2014), kg')
    con_temp = fields.Char('Concrete Temperature (°C)')
    des_wat_cem_rat = fields.Float('Design water-cement ratio (w/c)')
    slfl = fields.Char('Slump/Flow, mm (QCS 2014)')
    res_chl_ion = fields.Integer('Resistance to Chloride Ion Penetration ASTM C 1202 (Coulombs)')
    wat_pen = fields.Char('Water Penetration BSEN12390-8, mm')
    max_chl_mig = fields.Char('Maximum Chloride Migration, m²/s')
    wat_abs = fields.Integer('Water Absorption BS 1881 Part 122, %')

