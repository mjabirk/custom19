# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.osv import expression
import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    def _default_warehouse_id(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_id)])
        return warehouse[-1]

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='New', readonly=True)
    product_line_ids = fields.One2many('fleet.service.products', 'service_id', string="Items", copy=True)
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse",
                                   default=lambda self: self._default_warehouse_id(), check_company=True)
    picking_ids = fields.One2many('stock.picking', 'fleet_service_id', string='Transfers')
    purchase_ids = fields.One2many('purchase.order', 'fleet_service_id', string='Purchase Orders')
    move_ids = fields.One2many('account.move', 'fleet_service_id', string='Journal Entries')
    move_count = fields.Integer(string='Journal Entries Count', compute='_compute_account_move_ids')
    delivery_count = fields.Integer(string='Delivery Orders Count', compute='_compute_picking_ids')
    purchase_count = fields.Integer(string='Purchase Orders Count', compute='_compute_purchase_ids')
    expense_ids = fields.One2many('hr.expense', 'fleet_service_id', string='Expenses')
    expense_count = fields.Integer(string='Expenses Count', compute='_compute_expense_ids')
    total_cost = fields.Float(compute='_get_total_cost', string='Item Cost',digits=(16, 2), store=True)

    @api.onchange('total_cost')
    def total_cost_change(self):
        self.amount = self.total_cost



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
            self_comp = self.with_company(company_id)
            if vals.get('name', 'New') == 'New':
                service_date = None
                if 'date' in vals:
                    service_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date']))
                vals['name'] = self_comp.env['ir.sequence'].next_by_code('fleet.service', sequence_date=service_date) or '/'
        res = super(FleetVehicleLogServices, self).create(vals_list)
        return res

    @api.depends('product_line_ids')
    def _get_total_cost(self):
        res = {}
        for service in self:
            service.total_cost = 0
            for rec in service.product_line_ids:
                service.total_cost += rec.price_unit * rec.product_uom_qty

    @api.depends('move_ids')
    def _compute_account_move_ids(self):
        for service in self:
            service.move_count = len(service.move_ids)

    @api.depends('picking_ids')
    def _compute_picking_ids(self):
        for service in self:
            service.delivery_count = len(service.picking_ids)

    @api.depends('purchase_ids')
    def _compute_purchase_ids(self):
        for service in self:
            service.purchase_count = len(service.purchase_ids)

    @api.depends('expense_ids')
    def _compute_expense_ids(self):
        for service in self:
            service.expense_count = len(service.expense_ids)



    def action_view_expense(self):
        '''
        This function returns an action that display existing expenses
        of given service order ids. It can either be a in a list or in a form
        view, if there is only one expense to show.
        '''
        expense_ids = self.mapped('expense_ids')
        action = self.env["ir.actions.actions"]._for_xml_id("hr_expense.hr_expense_actions_all")
        if len(expense_ids) > 1:
            action['domain'] = [('id', 'in', expense_ids.ids)]
        elif len(expense_ids) == 1:
            form_view = [(self.env.ref('hr_expense.hr_expense_view_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state,view) for state,view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = expense_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_delivery(self):
        '''
        This function returns an action that display existing delivery orders
        of given service order ids. It can either be a in a list or in a form
        view, if there is only one delivery order to show.
        '''
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_picking_tree_all")

        pickings = self.mapped('picking_ids')
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
        elif pickings:
            form_view = [(self.env.ref('stock.view_picking_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = pickings.id
        # Prepare the context.
        picking_id = pickings.filtered(lambda l: l.picking_type_id.code == 'outgoing')
        if picking_id:
            picking_id = picking_id[0]
        else:
            picking_id = pickings[0]
        action['context'] = dict(self._context, default_picking_type_id=picking_id.picking_type_id.id,
                                 default_origin=self.name)
        return action

    def action_view_purchase(self):
        '''
        This function returns an action that display existing purchase orders
        of given service order.
        '''

        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("purchase.purchase_form_action")
        purchases = self.mapped('purchase_ids')
        action['domain'] = [('id', 'in', purchases.ids)]
        action['context'] = dict(self._context, create=False)
        return action

    def action_view_moves(self):
        '''
        This function returns an action that display existing accounting moves
        of given service order ids.
        '''

        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        moves = self.mapped('move_ids')
        action['domain'] = [('id', 'in', moves.ids)]
        action['context'] = dict(self._context, create=False)
        return action

    def create_expense(self):
        ''' Create the expenses from fleet.
         :return: An action redirecting to hr.expense tree/form view or True.
        '''

        product = self.env['product.product'].search([('can_be_expensed', '=', True)])
        if product:
            product = product.filtered(lambda p: p.default_code == "MAIN") or product[0]
        else:
            raise UserError(
                _("You need to have at least one product that can be expensed in your database to proceed!"))
        expenses = self.env['hr.expense']
        for line in self.product_line_ids:
            if line.procure_method == 'expense' and line.product_uom_qty > line.product_qty_ordered:
                expense = self.env['hr.expense'].create({
                    'name': self.name+' - '+line.name,
                    # 'unit_amount': line.price_unit,
                    # 'quantity':line.product_uom_qty - line.product_qty_ordered,
                    'total_amount':line.price_unit*(line.product_uom_qty - line.product_qty_ordered),
                    'total_amount_currency':line.price_unit*(line.product_uom_qty - line.product_qty_ordered),
                    'product_id': product.id,
                    'account_id':product.property_account_expense_id.id,
                    'fleet_service_id': self.id,
                    'fleet_service_line_id':line.id,
                    'employee_id':self.env.user.with_company(self.vehicle_id.company_id or self.env.company).employee_id.id,
                })
                expense.message_post(body=_('Uploaded Attachment'))
                expenses += expense
        if len(expenses) == 1:
            return {
                'name': _('Generated Expense'),
                'view_mode': 'form',
                'res_model': 'hr.expense',
                'type': 'ir.actions.act_window',
                'views': [[False, 'form']],
                'res_id': expenses[0].id,
            }
        elif expenses:
            return {
                'name': _('Generated Expenses'),
                'domain': [('id', 'in', expenses.ids)],
                'res_model': 'hr.expense',
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, "form"]],
            }
        return True

    # def create_journal(self):
    #     tot_debit = 0
    #     if self.env.company.service_expense_debit_account_id and self.env.company.service_expense_journal_id and self.env.company.service_expense_credit_account_id:
    #         for line in self.product_line_ids:
    #             if line.procure_method == 'cash' and line.accounted_amount < line.price_unit * line.product_uom_qty:
    #                 move_line = []
    #                 move_line.append({
    #                     'name': self.name+' - '+line.name,
    #                     'partner_id': line.partner_id and line.partner_id.id,
    #                     'account_id': self.env.company.service_expense_debit_account_id.id,
    #                     'journal_id': self.env.company.service_expense_journal_id.id,
    #                     'date': fields.Date.context_today(self),
    #                     'debit': line.price_unit * line.product_uom_qty - line.accounted_amount,
    #                     'credit': 0,
    #                 })
    #                 # tot_debit += line.price_unit * line.product_uom_qty - line.accounted_amount
    #                 move_line.append({
    #                     'name':  self.name+' - '+line.name,
    #                     'partner_id': False,
    #                     'account_id': self.env.company.service_expense_credit_account_id.id,
    #                     'journal_id': self.env.company.service_expense_journal_id.id,
    #                     'date': fields.Date.context_today(self),
    #                     'debit': 0,
    #                     'credit': line.price_unit * line.product_uom_qty - line.accounted_amount,
    #                 })
    #                 move_dict = {'narration': self.name+' - '+line.name,
    #                              'ref': 'Vehicle Service %s' % self.name,
    #                              'journal_id': self.env.company.service_expense_journal_id.id,
    #                              'date': fields.Date.context_today(self),
    #                              'fleet_service_id': self.id,
    #                              'line_ids': [(0, 0, line_vals) for line_vals in move_line]}
    #                 move_id = self.env['account.move'].create(move_dict)
    #                 move_id.action_post()
    #                 line.accounted_amount = line.price_unit * line.product_uom_qty
    #     return True

    def create_picking(self):
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'outgoing'), ('warehouse_id', '=', self.warehouse_id.id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'outgoing'), ('warehouse_id.company_id', '=', self.company_id.id)])
        if not picking_type:
            picking_type = self.env['stock.picking.type'].search(
                [('code', '=', 'outgoing'), ('warehouse_id', '=', False)])
        location_dest_id = self.env['stock.location'].search(
            [('usage', '=', 'production'), ('company_id', '=', self.company_id.id)])
        if not location_dest_id:
            location_dest_id = self.env['stock.location'].search(
                [('usage', '=', 'production'), ('company_id', '=', False)])
        location_id = picking_type[:1].default_location_src_id.id
        company_id = self.company_id.id or self.default_get(['company_id'])['company_id']
        store_move_vals = []
        purchase_line_vals = []
        for line in self.product_line_ids:
            if line.product_id and line.product_uom_qty > line.product_qty_ordered:
                if line.procure_method == 'store':
                    store_move_vals.append({
                        'name': line.product_id.display_name,
                        'product_id': line.product_id.id,
                        'location_id': location_id,
                        'location_dest_id': location_dest_id[:1].id,
                        'product_uom': line.product_uom.id,
                        'product_uom_qty': line.product_uom_qty - line.product_qty_ordered,
                        'partner_id': False,
                        'state': 'draft',
                        'fleet_service_line_id': line.id,
                        'company_id': company_id,
                        'origin': self.name,
                        'warehouse_id': self.warehouse_id.id
                    })
                elif line.procure_method == 'buy' and line.partner_id:
                    purchase_line_vals.append((line.partner_id, {
                        'name': line.name,
                        'product_qty': line.product_uom._compute_quantity(
                            line.product_uom_qty - line.product_qty_ordered, line.product_id.uom_po_id),
                        'product_id': line.product_id.id,
                        'product_uom': line.product_id.uom_po_id.id,
                        'price_unit': line.price_unit,
                        'date_planned': fields.Date.context_today(self),
                        'fleet_service_line_id': line.id,
                    }))
        if purchase_line_vals:
            purchase_orders = {}
            for purchase_line_val in purchase_line_vals:
                if purchase_line_val[0].id in purchase_orders.keys():
                    purchase_line_val[1]['order_id'] = purchase_orders[purchase_line_val[0].id]
                    self.env['purchase.order.line'].create(purchase_line_val[1])
                else:
                    purchase_vals = {
                        'partner_id': purchase_line_val[0].id,
                #        'partner_ref': purchase_line_val[0].ref,
                        'company_id': self.company_id.id,
                        'currency_id': self.env.company.currency_id.id,
                        'dest_address_id': False,  # False since only supported in stock
                        'origin': self.name,
                        'payment_term_id': purchase_line_val[0].property_supplier_payment_term_id.id,
                        'date_order': fields.Date.context_today(self),
                        'fleet_service_id': self.id
                    }
                    purchase_id = self.env['purchase.order'].create(purchase_vals)
                    purchase_orders[purchase_line_val[0].id] = purchase_id.id
                    purchase_line_val[1]['order_id'] = purchase_id.id
                    self.env['purchase.order.line'].create(purchase_line_val[1])
        if store_move_vals:
            vals = {
                'origin': self.name,
                'company_id': company_id,
                'move_type': 'direct',
                'picking_type_id': picking_type[:1].id,
                'location_id': location_id,
                'location_dest_id': location_dest_id[:1].id,
                'name': '/',
                'fleet_service_id': self.id
            }
            picking_id = self.env['stock.picking'].create(vals)
            for move_val in store_move_vals:
                move_val['picking_id'] = picking_id.id
                move_id = self.env['stock.move'].create(move_val)
                move_id._action_confirm()
                move_id._action_assign()
                # move_id.move_line_ids.qty_done = move_id.product_uom_qty
                move_id._action_done()
        return True


class FleetServiceProducts(models.Model):
    _name = 'fleet.service.products'
    _description = "Fleet Service Products"

    service_id = fields.Many2one('fleet.vehicle.log.services', string='Service', required=True, ondelete='cascade',
                                 index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    accounted_amount = fields.Float('Accounted Amount', digits='Product Price', default=0.0, readonly=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda x: x.env.company.currency_id)
    product_id = fields.Many2one('product.product', string='Product', change_default=True, ondelete='restrict', check_company=True, required=True)
    product_template_id = fields.Many2one('product.template', string='Product Template',
                                          related="product_id.product_tmpl_id")
    product_uom_qty = fields.Float(string='Product Quantity', digits='Product Unit of Measure', required=True,
                                   default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    company_id = fields.Many2one(related='service_id.company_id', string='Company', store=True, readonly=True,
                                 index=True)
    procure_method = fields.Selection([('store', 'Take from store'),
                                       ('buy', 'Purchase'),
                                       ('expense', 'Expense'),
                                       ('cash', 'Petty Cash'), ],
                                      string='Type', required=True, default='store')
    partner_id = fields.Many2one('res.partner', string='Vendor', readonly=False)
    move_ids = fields.One2many('stock.move', 'fleet_service_line_id', string='Stock Moves')
    purchase_line_ids = fields.One2many('purchase.order.line', 'fleet_service_line_id', string='Purchase Order Lines')
    product_qty_ordered = fields.Float(compute='_compute_qty_ordered', string="Quantity Ordered",
                                       digits='Product Unit of Measure', readonly=True, )
    expense_ids = fields.One2many('hr.expense', 'fleet_service_line_id', string='Expenses')

    @api.depends('product_uom_qty', 'move_ids', 'product_uom', 'product_id','expense_ids','purchase_line_ids')
    def _compute_qty_ordered(self):
        """Compute the visibility of the inventory widget."""
        for line in self:
            quantity = 0
            for move in line.move_ids:
                if move.picking_id.state != 'cancel' and move.product_id.id == line.product_id.id:
                    quantity += move.product_uom._compute_quantity(move.picking_id.state != 'done' and move.product_uom_qty or move.quantity, line.product_uom)
            for purchase_line in line.purchase_line_ids:
                if purchase_line.order_id.state != 'cancel' and purchase_line.product_id.id == line.product_id.id:
                    quantity += purchase_line.product_uom._compute_quantity(purchase_line.product_qty, line.product_uom)
            for expense in line.expense_ids:
                quantity += expense.quantity
            line.product_qty_ordered = quantity

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Compute the amounts of the line.
        """
        for line in self:
            price = line.price_unit * line.product_uom_qty
            line.update({
                'price_subtotal': price,
            })

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        self.price_unit = self.product_id.standard_price

    @api.onchange('product_id')
    def product_uom_change(self):
        if not self.product_id:
            self.price_unit = 0.0
            return
        self.product_uom = self.product_id.uom_po_id.id
        self.product_uom_qty = self.product_uom_qty or 1.0
        self.name = self.product_id.display_name
        self.price_unit = self.product_id.standard_price


class AccountMove(models.Model):
    _inherit = "account.move"
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services', string="Fleet Service", readonly=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
