# # -*- coding: utf-8 -*-
#
# from odoo import models
# class MixProportionsXlsx(models.AbstractModel):
#     _name = 'report.analysis_reports.mix_proportions'
#     _inherit = 'report.report_xlsx.abstract'
#     def generate_xlsx_report(self, workbook, data, bom):
#         for obj in bom:
#             report_name = obj.product_tmpl_id.default_code or obj.product_tmpl_id.name
#             # One sheet by BOM
#             sheet = workbook.add_worksheet(report_name[:31])
#             format1 = workbook.add_format({'font_size': 22, 'bg_color': '#B8F2FC','bold': True,'border':1,})
#             format2 = workbook.add_format({'font_size': 16, 'bg_color': '#B8F2FC','bold': True,'border':1,})
#             format3 = workbook.add_format({'font_size': 12, 'bg_color': '#B8F2FC','bold': True,'border':1,})
#             format4 = workbook.add_format({'font_size': 12, 'bg_color': '#B8F2FC','bold': True,'border':1,'num_format': '0.0'})
#             format2.set_text_wrap()
#             format3.set_text_wrap()
#             sheet.merge_range('A1:H1', "MIX PROPORTIONS", format1)
#             sheet.write(1, 0, 'Materials', format2)
#             sheet.write(1, 1, 'Source', format2)
#             sheet.write(1, 2, 'Batch Weight (SSD), kg/m3', format2)
#             sheet.write(1, 3, 'Absorption, %', format2)
#             sheet.write(1, 4, 'Water Correction, kg/m3', format2)
#             sheet.write(1, 5, 'Batch Weight (Dry), kg/m³', format2)
#             sheet.write(1, 6, 'Spec. Gravity', format2)
#             sheet.write(1, 7, 'Absolute Volume, m³', format2)
#             sheet.set_row(1, 40)
#             sheet.set_column(0,0,40)
#             sheet.set_column(1,7,18)
#             line_no = 1
#             batch_tot = wc_tot = dry_wt = ab_vol = 0
#             for line in obj.bom_line_ids:
#                 line_no += 1
#                 sheet.write(line_no, 0, line.product_id.name, format3)
#                 sheet.write(line_no, 1, line.product_id.seller_ids and line.product_id.seller_ids[0].name.name or '', format3)
#                 sheet.write(line_no, 2, line.product_qty, format3)
#                 sheet.write(line_no, 3, line.absorption_pc, format3)
#                 sheet.write(line_no, 4, line.product_qty*line.absorption_pc/100, format3)
#                 sheet.write(line_no, 5, line.product_qty - line.product_qty*line.absorption_pc/100, format3)
#                 sheet.write(line_no, 6, line.spec_gravity, format3)
#                 sheet.write(line_no, 7, line.spec_gravity and line.product_qty/line.spec_gravity/1000 or 0, format3)
#                 batch_tot += line.product_qty
#                 wc_tot += line.product_qty*line.absorption_pc/100
#                 dry_wt += line.product_qty - line.product_qty*line.absorption_pc/100
#                 ab_vol += line.spec_gravity and line.product_qty/line.spec_gravity/1000 or 0
#             line_no += 1
#             sheet.merge_range('A%s:B%s'%(line_no+1,line_no+1), "Total Weight, kg/m3", format1)
#             sheet.write(line_no, 2, batch_tot, format3)
#             sheet.write(line_no, 3, '', format3)
#             sheet.write(line_no, 4, wc_tot, format3)
#             sheet.write(line_no, 5, dry_wt, format3)
#             sheet.merge_range('G%s:H%s'%(line_no+1,line_no+1), "Air Content = (2%)", format1)
#             line_no += 1
#             sheet.merge_range('A%s:B%s'%(line_no+1,line_no+1), "Total Volume, m³", format1)
#             sheet.write(line_no, 2, '', format3)
#             sheet.write(line_no, 3, '', format3)
#             sheet.write(line_no, 4, '', format3)
#             sheet.write(line_no, 5, '', format3)
#             sheet.write(line_no, 6, '', format3)
#             sheet.write(line_no, 7, ab_vol+2/100, format4)