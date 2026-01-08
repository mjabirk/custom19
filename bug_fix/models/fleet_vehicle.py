# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.osv import expression



class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=None, order=None):
        domain = domain or []
        if name:
            name_domain = ['|', '|', '|', ('name', operator, name), ('license_plate', operator, name),
                      ('x_studio_woqod_number', operator, name), ('x_studio_vehicle_code', operator, name),]
            return self._search(expression.AND([name_domain, domain]), limit=limit, order=order)
        return super()._name_search(name, domain, operator, limit, order)


    @api.depends('model_id.brand_id.name', 'model_id.name', 'license_plate', 'x_studio_vehicle_code')
    def _compute_vehicle_name(self):
        super(FleetVehicle, self)._compute_vehicle_name()
        update_all = False
        for record in self:
            if record.co2_standard == 'A@LL':
                update_all = True
        if not update_all:
            for record in self:
                if record.x_studio_vehicle_code:
                    record.name = (record.model_id.brand_id.name or '') + '/' + (record.model_id.name or '') + '/' + (
                                record.license_plate or _('No Plate')) + '/' + (record.x_studio_vehicle_code or '')
        else:
            vehicles = self.search([])
            for record in vehicles:
                if record.x_studio_vehicle_code:
                    record.name = (record.model_id.brand_id.name or '') + '/' + (record.model_id.name or '') + '/' + (
                                record.license_plate or _('No Plate')) + '/' + (record.x_studio_vehicle_code or '')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: