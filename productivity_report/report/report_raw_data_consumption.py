# -*- coding:utf-8 -*-

from odoo import api, models, _, fields
from odoo.exceptions import UserError


class ReportRawDataCons(models.AbstractModel):
    _name = 'report.productivity_report.report_raw_data_consumption'
    _description = "Raw Data Consumption"
    def get_data(self, form):
        product_list = {}
        based_on = form.get('based_on', False)
        start_date = form.get('start_date', False)
        end_date = form.get('end_date', False)
        delivery_names = []
        if based_on == 'date':
            query = """select x_item_code, sum(x_quantity )  from x_alkon_raw_data 
                        WHERE x_date >= %s and x_date <= %s  and x_record_type = 'Inventory' and x_inventory_trans_type in ('A','U') group by x_item_code"""
            self._cr.execute(query, (start_date, end_date))
            for product, quantity in self._cr.fetchall():
                if product:
                    if product_list.get(product):
                        product_list[product]['raw_data_qty'] -= quantity
                    else:
                        product_list[product] = {'raw_data_qty':-1*quantity,
                                                 'odoo_qty':0}
            picking_types = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
            query = """select p.default_code, sum(l.qty_done )  from stock_move_line l join product_product p on p.id = l.product_id join stock_picking pick on l.picking_id = pick.id
                        WHERE pick.date_done >= %s and pick.date_done <= %s  and l.state = 'done' and pick.picking_type_id in %s group by p.default_code"""
            self._cr.execute(query, (start_date, end_date,tuple(picking_types.ids)))
            for product, quantity in self._cr.fetchall():
                if product:
                    if product_list.get(product):
                        product_list[product]['odoo_qty'] += quantity
                    else:
                        product_list[product] = {'raw_data_qty':0,
                                                 'odoo_qty':quantity}
        else:
            picking_types = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
            query = """select p.default_code, sum(l.qty_done )  from stock_move_line l join product_product p on p.id = l.product_id join stock_picking pick on l.picking_id = pick.id
                                    WHERE pick.date_done >= %s and pick.date_done <= %s  and l.state = 'done' and pick.picking_type_id in %s group by p.default_code"""
            self._cr.execute(query, (start_date, end_date, tuple(picking_types.ids)))
            for product, quantity in self._cr.fetchall():
                if product:
                    if product_list.get(product):
                        product_list[product]['odoo_qty'] += quantity
                    else:
                        product_list[product] = {'raw_data_qty': 0,
                                                 'odoo_qty': quantity}
            query = """select name  from  stock_picking WHERE date_done >= %s and date_done <= %s  and state = 'done' and picking_type_id in %s"""
            self._cr.execute(query, (start_date, end_date, tuple(picking_types.ids)))
            delivery_names = self._cr.fetchall()
            delivery_names = tuple([x[0] for x in delivery_names])
            if delivery_names:
                query = """select x_item_code, sum(x_quantity )  from x_alkon_raw_data 
                            WHERE x_studio_delivery_ref_dn in %s and x_record_type = 'Inventory' and x_inventory_trans_type in ('A','U') group by x_item_code"""
                self._cr.execute(query, (delivery_names,),)
                for product, quantity in self._cr.fetchall():
                    if product:
                        if product_list.get(product):
                            product_list[product]['raw_data_qty'] -= quantity
                        else:
                            product_list[product] = {'raw_data_qty':-1*quantity,
                                                     'odoo_qty':0}
        return (product_list,delivery_names)
    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        get_data,delivery_numbers = self.get_data(data['form'])
        return {
            'doc_ids': docids,
            'doc_model': model,
            'data': data,
            'docs': docs,
            'get_data': get_data,
            'get_delivery_names':delivery_numbers,
        }
