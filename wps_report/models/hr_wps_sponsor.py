from odoo import models, fields, api


class HrWpsSponsor(models.Model):
    """
    Holds Qatar WPS sponsor information, linked to a partner (company or person).
    """
    _name = 'hr.wps.sponsor'
    _description = 'HR WPS Sponsor'
    _rec_name = 'display_name'  # This makes it show a useful name in dropdowns

    # This is the "Sponsor Name" you asked for.
    # We link to 'res.partner' because a sponsor is a contact (company or person).
    partner_id = fields.Many2one(
        'res.partner',
        string="Sponsor (Contact)",
        required=True,
        ondelete='restrict',
        help="The company or individual sponsoring the employees."
    )

    # This computed field makes the name more descriptive
    display_name = fields.Char(
        string="Display Name",
        compute='_compute_display_name',
        store=True
    )
    bank_account_id = fields.Many2one('res.partner.bank',  string="Bank Account", required=True)

    employer_eid = fields.Char(string="Employer EID")
    payer_eid = fields.Char(string="Payer EID")
    payer_qid = fields.Char(string="Payer QID")

    # This is the One2many field to see all linked employees
    employee_ids = fields.One2many(
        'hr.employee',
        'wps_sponsor_id',
        string="Sponsored Employees"
    )

    employee_count = fields.Integer(
        compute='_compute_employee_count',
        string="Employee Count"
    )
    additional_header = fields.Char('Additional Header', size=64,help='Additional Header for HSBC Bank. Add entires in coma seperated format. Eg:QAWPS,ABC19361001,P,R%m%M,%y%m%d,W01')
    _sql_constraints = [
        ('partner_id_uniq', 'unique(partner_id)',
         'A contact (partner) can only be linked to one WPS Sponsor record.')
    ]

    @api.depends('partner_id.name', 'employer_eid')
    def _compute_display_name(self):
        """ Creates a name like 'Sponsor Company Name [12345]' """
        for record in self:
            name = record.partner_id.name or 'New'
            if record.employer_eid:
                record.display_name = f"{name} [{record.employer_eid}]"
            else:
                record.display_name = name

    def _compute_employee_count(self):
        for record in self:
            record.employee_count = len(record.employee_ids)