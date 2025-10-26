from odoo import api, models, fields


class HrVersion(models.Model):
    _inherit = 'hr.version'

    accommodation_allowance = fields.Monetary('Accommodation Allowance', default=0, tracking=True, help="Monthly Accommodation Allowance.")
    food_allowance = fields.Monetary('Food Allowance', default=0, tracking=True, help="Monthly Food Allowance.")
    transportation_allowance = fields.Monetary('Transportation Allowance', default=0, tracking=True, help="Monthly Transportation Allowance.")
    other_allowance = fields.Monetary('Other Allowance', default=0, tracking=True, help="Monthly Other Allowance.")
    rp_charge = fields.Monetary('RP Charge', default=0, tracking=True)
    air_ticket = fields.Monetary('Air Ticket', default=0, tracking=True)
    leave_pay_days = fields.Integer("Leave Pay Days")
    eos_days = fields.Integer("End Of Service Days")
    leave_period = fields.Integer("Leave Period")
    leave_accrual_amount = fields.Monetary("Leave pay Accrual per Day", compute='_compute_accrual_amount')
    eos_accrual_amount = fields.Monetary("EOS Accrual per Day", compute='_compute_accrual_amount')
    total_salary = fields.Monetary('Total Salary', compute='_compute_total_salary', store=True, tracking=True, help="Total monthly salary including wage and all allowances.")

    @api.depends('wage', 'accommodation_allowance', 'food_allowance', 'transportation_allowance', 'other_allowance')
    def _compute_total_salary(self):
        """
        Calculates the total salary by summing the basic wage and all allowances.
        """
        for contract in self:
            contract.total_salary = (
                contract.wage +
                contract.accommodation_allowance +
                contract.food_allowance +
                contract.transportation_allowance +
                contract.other_allowance
            )

    @api.depends('leave_pay_days', 'eos_days', 'wage', 'accommodation_allowance')
    def _compute_accrual_amount(self):
        days_per_month = 365/12
        for record in self:
            record.eos_accrual_amount = (record.wage / days_per_month) * record.eos_days / 365
            record.leave_accrual_amount = ((record.wage + record.accommodation_allowance) / days_per_month) * record.leave_pay_days / 365

    @api.model
    def _get_whitelist_fields_from_template(self):
        whitelisted_fields = super()._get_whitelist_fields_from_template() or []
        if self.env.company.country_id.code == "QA":
            whitelisted_fields += [
                "accommodation_allowance",
                "food_allowance",
                "transportation_allowance",
                "other_allowance",
                "rp_charge",
                "air_ticket",
                "leave_pay_days",
                "eos_days",
                "leave_period",
            ]
        return whitelisted_fields
