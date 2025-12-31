# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class OfferLetter(models.Model):
    _name = 'offer.letter'
    _description = 'Offer Letter'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    reference = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: _('New')
    )
    date = fields.Date(string='Date')
    name = fields.Char(string='Name')
    name_ar = fields.Char(string='Name (Arabic)')
    active = fields.Boolean(string='Active', default=True)
    job_arabic = fields.Char(string='Job (Arabic)', compute="_compute_job_arabic", store=True)
    job_id = fields.Many2one('hr.job', string='Job')
    nationality = fields.Many2one('res.country', string='Nationality')
    arabic_country = fields.Char(string='Arabic Country', compute="_compute_arabic_country", store=True)
    id_no = fields.Char(string='ID Number')
    probationary_period = fields.Integer(string='Probationary Period')
    annual_leave_and_tickets = fields.Integer(string='Annual Leave and Tickets')
    leaves = fields.Selection(
        [('1', 'Every 1 Year'), ('2', 'Every 2 Year')],
        string='Leaves'
    )
    comments = fields.Char(string='Comments')
    comments_ar = fields.Char(string='Comments (Arabic)')
    contract_period = fields.Integer(string='Contract Period(Year)')
    contract_type = fields.Many2one('hr.contract.type', string='Contract Type')
    contract_type_ar = fields.Char(string='Contract Type (Arabic)', compute="_compute_contract_type_ar", store=True)
    basic_salary = fields.Monetary(string='Basic Salary')
    accommodation = fields.Monetary(string='Accommodation')
    transportation = fields.Monetary(string='Transportation Allowance')
    others = fields.Monetary(string='Others')
    total_offer = fields.Monetary(
        string='Total',
        compute="_compute_total_offer",
        store=True
    )
    approved_date = fields.Date(string='Approved Date', readonly=True)
    approved_user = fields.Many2one('res.users', string='Approved User', readonly=True)
    # Default currency taken from company
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
        required=True
    )
    state = fields.Selection(
        [('draft', 'New'), ('approved', 'Approved')],
        string='Status', default='draft', tracking=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company.id,
        required=True
    )
    location = fields.Char(string='Location')
    notes = fields.Html(string='Notes')

    # -------------------
    # COMPUTES
    # -------------------
    @api.depends('basic_salary', 'accommodation', 'others','transportation')
    def _compute_total_offer(self):
        for rec in self:
            rec.total_offer = (rec.basic_salary or 0.0) + (rec.accommodation or 0.0) + (rec.others or 0.0) + (rec.transportation or 0.0)

    @api.depends('contract_type')
    def _compute_contract_type_ar(self):
        """Auto-calculate Arabic contract type name."""
        for record in self:
            if record.contract_type:
                record.contract_type_ar = record.contract_type.with_context(lang='ar_001').name
            else:
                record.contract_type_ar = ''

    @api.depends('nationality')
    def _compute_arabic_country(self):
        """Auto-calculate Arabic country name based on nationality."""
        for record in self:
            if record.nationality:
                record.arabic_country = record.nationality.with_context(lang='ar_001').name
            else:
                record.arabic_country = ''

    @api.depends('job_id')
    def _compute_job_arabic(self):
        """Auto-calculate job_arabic name based on job_id."""
        for record in self:
            if record.job_id:
                record.job_arabic = record.job_id.with_context(lang='ar_001').name
            else:
                record.job_arabic = ''

    # -------------------
    # CREATE
    # -------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('reference', _('New')) == _('New'):
                vals['reference'] = self.env['ir.sequence'].next_by_code('offer.letter') or _('New')
            if not vals.get('company_id'):
                vals['company_id'] = self.env.company.id
        return super(OfferLetter, self).create(vals_list)

    # -------------------
    # ACTIONS
    # -------------------
    def action_approve(self):
        """Sets the offer letter state to 'Approved', assigns date and user."""
        self.write({
            'state': 'approved',
            'approved_date': date.today(),
            'approved_user': self.env.user.id,
        })

    def action_draft(self):
        """Resets the offer letter to 'Draft' state."""
        self.write({'state': 'draft'})

    def action_print_with_header(self):
        return self.env.ref('offer_letter.action_report_offer_letter').report_action(self)

    def action_print_without_header(self):
        return self.env.ref('offer_letter.action_report_offer_letter_no_header').report_action(self)

    # -------------------
    # READONLY LOGIC
    # -------------------
    @api.onchange('state')
    def _onchange_state(self):
        """Make all fields readonly when state is approved."""
        if self.state == 'approved':
            for field_name, field in self._fields.items():
                if field_name not in ['state', 'approved_date', 'approved_user']:
                    field.readonly = True
        else:
            for field_name, field in self._fields.items():
                field.readonly = field.readonly