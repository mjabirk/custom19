# -*- coding: utf-8 -*-

from odoo import api, models, fields
#from datetime import datetime, timedelta
import pytz

class WoqodRawData(models.Model):
    _name = 'woqod.raw.data'
    _description = "Woqod Raw Data"

    name = fields.Char(string='Station Name')
    date = fields.Datetime(string='Sale Time')
    license_plate = fields.Char(string='License Plate')
    product_name = fields.Char(string='Product Name')
    total_amount = fields.Float(string='Total Amount (Qar)')
    unit_price = fields.Float(string='Unit Price (QAR/Lt)')
    liter = fields.Float(string='Liter (lt)')
    processed = fields.Boolean(string='Processed', default=False)
    notes = fields.Text(string='Note')
    vehicle_service_id = fields.Many2one('fleet.vehicle.log.services', string='Service', required=False, readonly=True)

    def process_data(self):
        service_type_list = {}
        local_context_tz = pytz.timezone('Asia/Qatar')
        utc_context_tz = pytz.timezone('UTC')
        for rec_id in self.search([('processed','=',False)]):
            vehicle_id = service_type = False
            service_type_id = service_type_list.get(rec_id.product_name)
            if not service_type_id:
                service_type = self.env['fleet.service.type'].search([('name', '=', rec_id.product_name)],limit=1)
                if not service_type:
                    service_type = self.env['fleet.service.type'].search([('name', 'in', 'DIESEL' in rec_id.product_name.upper() and ('Diesel','DIESEL') or ('SILVER' in rec_id.product_name.upper() or 'GOLD' in rec_id.product_name.upper()) and ('Petrol','PETROL'))],limit=1)
                if not service_type:
                    service_type = self.env['fleet.service.type'].search([('name', '=', 'Refueling')],limit=1)
                if service_type:
                    service_type_id = service_type_list[rec_id.product_name] = service_type.id
            vehicle_id = self.env['fleet.vehicle'].search(['|', ('license_plate', '=', rec_id.license_plate),('woqod_number', '=', rec_id.license_plate)],limit=1)
            if vehicle_id and service_type_id:
                duplicate_ids =self.env['fleet.vehicle.log.services'].search([('vehicle_id','=',vehicle_id.id),
                                                                              ('quantity','=',rec_id.liter),
                                                                              ('amount','=',rec_id.total_amount),
                                                                              ('starting_time','=',rec_id.date)]) # and rec_id.date.replace(tzinfo=utc_context_tz).astimezone(local_context_tz)
                if not duplicate_ids:
                    service_id = self.env['fleet.vehicle.log.services'].create({
                        'description': 'Refuel - %s'%(rec_id.name),
                        'vehicle_id': vehicle_id.id,
                        'service_type_id': service_type_id,
                        'date': rec_id.date,# and rec_id.date.replace(tzinfo=utc_context_tz).astimezone(local_context_tz),.replace(tzinfo=None)
                        'quantity': rec_id.liter,
                        'amount': rec_id.total_amount,
                        'starting_time':rec_id.date,
                        'woqod_rawdata_id':rec_id.id,
                        })
                    rec_id.write({'processed':True,'vehicle_service_id':service_id.id})
                else:
                    rec_id.write({'notes': 'Duplicate records found with ids %s.'%(str([x.id for x in duplicate_ids]))})
            else:
                message = ''
                if not vehicle_id:
                    message += 'Unable to find vehicle'
                if not service_type_id:
                    message += 'Unable to find service type for %s. Please create a service type with this name or Refueling from menu Fleet / Configuration / Service Types'%(rec_id.product_name)
                rec_id.write({'notes': message})


    class FleetVehicle(models.Model):
        _inherit = 'fleet.vehicle'
        woqod_number = fields.Char(string='Woqod Number')

    class FleetVehicleLogServices(models.Model):
        _inherit = 'fleet.vehicle.log.services'
        quantity = fields.Float(string='Quantity', digits=(16, 2))
        starting_time = fields.Datetime(string='Starting Time')
        woqod_rawdata_id =  fields.Many2one('woqod.raw.data', string='Service', required=False,)




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: