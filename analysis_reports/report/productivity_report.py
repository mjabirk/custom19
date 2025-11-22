# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools.sql import drop_view_if_exists


class ProductivityReport(models.Model):
    _name = "productivity.report"
    _description = "Productivity Analysis"
    _auto = False

    date = fields.Date(string='Date', readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle', required=True, readonly=True)
    active = fields.Boolean('Active', readonly=True)
    vehicle_code = fields.Char('Vehicle Code')
    license_plate = fields.Char('License Plate')
    employee_id = fields.Many2one('hr.employee', string='Driver', readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    trips = fields.Float(string='Trips', readonly=True)
    fuel = fields.Float(string='Fuel (Liter)', readonly=True)
    fuel_cost = fields.Float(string='Fuel Cost', readonly=True)
    service = fields.Float(string='Service Cost', readonly=True)
    distance = fields.Float(string='Distance Travelled', readonly=True)
    planned_distance = fields.Float(string='Planned Distance', readonly=True)
    worked_time = fields.Float(string='Hour', readonly=True)
    type = fields.Selection([('trips','Trips'),
                             ('fuel', 'Fuel'),
                             ('service', 'Service')], readonly=True)

    def init(self):
        drop_view_if_exists(self.env.cr, self._table)

        self.env.cr.execute("""
            create or replace view productivity_report as (
                select
                    row_number() OVER () AS id,
                    vehicle_id,
                    vehicle_code,
                    active,
                    license_plate,
                    employee_id,
                    quantity,
                    trips,
                    fuel,
                    fuel_cost,
                    service,
                    distance,
                    planned_distance,
                    worked_time,
                    date,
                    type
                from ( 
                         select x_vehicle_id as vehicle_id,
                        ve.x_studio_vehicle_code as vehicle_code,
                        ve.active,
                        ve.license_plate as license_plate,
                        x_employee_id as employee_id,
                        x_quantity as quantity,
                        x_trips as trips,
                        0 as fuel,
                        0 as fuel_cost,
                        0 as service,
                        0 as distance,
                        pr.x_studio_planned_distance as planned_distance,
                    ---    (select sum(x_studio_distance_km) from x_alkon_raw_data where x_productivity_id = pr.id) as planned_distance,
                        0 as worked_time,
                        pr.x_date as date,
                        'trips' as type
                        from
                        x_productivity_record pr,
                        fleet_vehicle ve
                        where pr.x_vehicle_id = ve.id
                        union all
                        
                        select vehicle_id,
                        ve.x_studio_vehicle_code as vehicle_code,
                        ve.active,
                        ve.license_plate as license_plate,
                        NULL as employee_id,
                        0 as quantity,
                        0 as trips,
                        quantity as fuel,
                        amount as fuel_cost,
                        0 as service,
                        0 as distance,
                        0 as planned_distance,
                        0 as worked_time,
                        date,
                        'fuel' as type
                        from
                        fleet_vehicle_log_services fs,
                        fleet_vehicle ve
                        where fs.vehicle_id = ve.id
                        and service_type_id in (select id from fleet_service_type where name->>'en_US' in ('Petrol','Diesel'))
                        union all	
                        
                        
                        select vehicle_id,
                        ve.x_studio_vehicle_code as vehicle_code,
                        ve.active,
                        ve.license_plate as license_plate,
                        NULL as employee_id,
                        0 as quantity,
                        0 as trips,
                        0 as fuel,
                        0 as fuel_cost,
                        amount as service,
                        0 as distance,
                        0 as planned_distance,
                        0 as worked_time,
                        date,
                        'service' as type
                        from
                        fleet_vehicle_log_services fs,
                        fleet_vehicle ve
                        where fs.vehicle_id = ve.id
                        and service_type_id in (select id from fleet_service_type where name->>'en_US' not in ('Petrol','Diesel'))
                        union all	
                        
                        
                        select vehicle_id,
                        ve.x_studio_vehicle_code as vehicle_code,
                        ve.active,
                        ve.license_plate as license_plate,
                        NULL as employee_id,
                        0 as quantity,
                        0 as trips,
                        0 as fuel,
                        0 as fuel_cost,
                        0 as service,
                        x_studio_distance_travelled as distance,
                        0 as planned_distance,
                        x_studio_worked_time as worked_time,
                        date,
                        'trips' as type
                        from
                        fleet_vehicle_odometer od,
                        fleet_vehicle ve
                        where od.vehicle_id = ve.id
                        
                        
     
                        
                         
                         )AS tempTable  
            )
        """)


# select
# vehicle_id,
# ve.x_studio_vehicle_code as vehicle_code,
# ve.active,
# ve.license_plate as license_plate,
# NULL as employee_id,
# 0 as quantity,
# 0 as trips,
# 0 as fuel,
# 0 as fuel_cost,
# 0 as service,
# x_studio_distance_travelled as distance,
# x_studio_worked_time as worked_time,
# date,
# 'trips' as type
# from
#
# fleet_vehicle_odometer
# od,
# fleet_vehicle
# ve
# where
# od.vehicle_id = ve.id
