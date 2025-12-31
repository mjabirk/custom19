# -*- coding: utf-8 -*-

from odoo import api, models, fields
from odoo.fields import Datetime
from dateutil.relativedelta import relativedelta
from odoo.tools import float_round

class CustomerDocumentLines(models.Model):
    _name = 'customer.evaluation.lines'
    _rec_name = 'partner_id'
    _description = "Customer Evaluation Lines"
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    last_invoice_date = fields.Date('Last invoice date', readonly=False)
    first_invoice_date = fields.Date('First invoice date', readonly=False)
    turnover_360_days = fields.Float(string='Last 360 days turnover', readonly=False)
    turnover_180_days = fields.Float(string='Last 180 days turnover', readonly=False)
    total_turnover = fields.Float(string='Total turnover', readonly=False)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    active = fields.Boolean(default=True)
    total_due = fields.Monetary(string='Total Due')
    currency_id = fields.Many2one('res.currency',related='partner_id.currency_id')


class CustomerSuspiciousActivity(models.Model):
    _name = 'customer.suspicious.activity'
    _rec_name = 'partner_id'
    _description = "Suspicious Activity"
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date = fields.Date('Date', readonly=False)
    action = fields.Char(string="Action")
    reason = fields.Char(string="Given Reason")

class Partner(models.Model):
    _inherit = 'res.partner'
    customer_evaluation_line_ids = fields.One2many(comodel_name='customer.evaluation.lines', inverse_name='partner_id')
    customer_suspicious_line_ids = fields.One2many(comodel_name='customer.suspicious.activity', inverse_name='partner_id')
    last_invoice_date = fields.Date('Last invoice date', compute='_compute_evaluation_data',  search='_search_last_invoice_date', readonly=True, store=False)
    first_invoice_date = fields.Date('First invoice date', compute='_compute_evaluation_data', search='_search_first_invoice_date', readonly=True, store=False)
    turnover_360_days = fields.Float(string='Last 360 days turnover', compute='_compute_evaluation_data', search='_search_turnover_360', readonly=True, store=False)
    turnover_180_days = fields.Float(string='Last 180 days turnover', compute='_compute_evaluation_data', search='_search_turnover_180', readonly=True, store=False)
    total_turnover = fields.Float(string='Total turnover', compute='_compute_evaluation_data', search='_search_turnover_total', readonly=True, store=False)
    available_credit = fields.Monetary(string="Available Credit", currency_field='currency_id', compute='_compute_available_credit',
                                       store=False,  compute_sudo=True,)

    def _compute_available_credit(self):
        for partner in self:
            company = self.env.company
            partner_sudo = partner.with_company(company).sudo()
            credit_limit = partner_sudo.credit_limit or 0.0
            quotation_total = 0
            receivable_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner_sudo.id),
                ('account_id.account_type', '=', 'asset_receivable'),
                ('company_id', '=', company.id),
                ('move_id.state', '=', 'posted'),
            ])
            customer_balance = sum(receivable_lines.mapped('amount_residual'))
            confirmed_sales = partner_sudo.sale_order_ids.filtered(
                lambda o: o.state == 'sale'
                          and o.company_id == company
                          and all(line.qty_delivered == 0 for line in o.order_line)
            )
            confirmed_sales_total = sum(confirmed_sales.mapped('amount_total'))
            draft_payments = self.env['account.payment'].search([
                ('partner_id', '=', partner_sudo.id),
                ('state', '=', 'draft'),
                ('company_id', '=', company.id),
                ('guarantee_check', '!=', True)
            ])
            draft_payments_total = sum(draft_payments.mapped('amount'))
            partner.available_credit = credit_limit + draft_payments_total - quotation_total - customer_balance - confirmed_sales_total

    @api.depends(
        'customer_evaluation_line_ids.last_invoice_date',
        'customer_evaluation_line_ids.first_invoice_date',
        'customer_evaluation_line_ids.turnover_360_days',
        'customer_evaluation_line_ids.turnover_180_days',
        'customer_evaluation_line_ids.total_turnover',)

    def _compute_evaluation_data(self):
        for record in self:
            last_invoice_date = first_invoice_date = False
            turnover_360_days = turnover_180_days = total_turnover = tot_due=0
            for line in record.customer_evaluation_line_ids:
                last_invoice_date = (line.last_invoice_date and last_invoice_date) and max(last_invoice_date,line.last_invoice_date) or line.last_invoice_date or last_invoice_date
                first_invoice_date = (first_invoice_date and line.last_invoice_date) and min(first_invoice_date,line.first_invoice_date) or line.first_invoice_date or first_invoice_date
                turnover_360_days += line.turnover_360_days
                turnover_180_days += line.turnover_180_days
                total_turnover += line.total_turnover
                tot_due += line.total_due
            record.last_invoice_date = last_invoice_date
            record.first_invoice_date = first_invoice_date
            record.turnover_360_days = turnover_360_days
            record.turnover_180_days = turnover_180_days
            record.total_turnover = total_turnover

    def _search_last_invoice_date(self, operator, value):
        eval_lines = self.env['customer.evaluation.lines'].search([('last_invoice_date', operator, value),])
        return [('id', 'in', eval_lines.mapped('partner_id').ids)]

    def _search_first_invoice_date(self, operator, value):
        eval_lines = self.env['customer.evaluation.lines'].search([('first_invoice_date', operator, value),])
        return [('id', 'in', eval_lines.mapped('partner_id').ids)]

    def _search_turnover_360(self, operator, value):
        eval_lines = self.env['customer.evaluation.lines'].search([('turnover_360_days', operator, value),])
        return [('id', 'in', eval_lines.mapped('partner_id').ids)]

    def _search_turnover_180(self, operator, value):
        eval_lines = self.env['customer.evaluation.lines'].search([('turnover_180_days', operator, value),])
        return [('id', 'in', eval_lines.mapped('partner_id').ids)]

    def _search_turnover_total(self, operator, value):
        eval_lines = self.env['customer.evaluation.lines'].search([('turnover_180_days', operator, value),])
        return [('id', 'in', eval_lines.mapped('partner_id').ids)]

    def compute_evaluation_lines(self):
        customer = self.env['res.partner'].search([('parent_id', '=', False)])
        if customer:
            query = """
                SELECT m.partner_id,m.company_id,  max(m.invoice_date), min(m.invoice_date)
                      FROM account_move m WHERE m.move_type = 'out_invoice' AND m.state='posted'
                      AND m.partner_id IN %(partner_ids)s
                      AND m.company_id IN %(company_ids)s
                      GROUP BY m.partner_id, m.company_id
                      """
            params = {
                    'partner_ids': tuple(customer.ids),
                    'company_ids': tuple(self.env.companies.ids),
                }
            self.env.cr.execute(query, params)
            for record in self.env.cr.dictfetchall():
                evaluation_line = self.env['customer.evaluation.lines'].search([('active', '=', True), ('partner_id', '=', record['partner_id']), ('company_id', '=',record['company_id'])])
                if not evaluation_line:
                    self.env['customer.evaluation.lines'].create({'partner_id':record['partner_id'],
                                                                  'company_id':record['company_id'],
                                                                  'first_invoice_date':record['min'],
                                                                  'last_invoice_date':record['max']})
                else:
                    evaluation_line.first_invoice_date = record['min']
                    evaluation_line.last_invoice_date = record['max']
            query="""SELECT partner_id, 
            company_id, 
            sum(turnover_180) as turnover_180, 
            sum(turnover_360) as turnover_360, 
            sum(total_turnover) as total_turnover,
            sum(tot_due) as tot_due
              FROM (
                      SELECT
                      l.partner_id, 
                      inv.company_id, 
                      SUM(l.debit - l.credit) as turnover_180, 
                      0 as turnover_360, 
                      0 as total_turnover,
                      0 as tot_due
                      FROM account_move_line l
                      LEFT JOIN account_move inv ON l.move_id = inv.id
                      LEFT JOIN account_account acc ON l.account_id = acc.id
                      WHERE
                      l.partner_id IN %(partner_ids)s
                      AND l.date >= %(date_from_180)s
                      AND l.date <= %(date_to)s
                      AND l.company_id IN %(company_ids)s
                      AND inv.state = 'posted'
                      AND acc.account_type in ('asset_receivable')
                      AND inv.move_type IN ('out_refund', 'out_invoice')
                      GROUP BY l.partner_id, inv.company_id  
                  union all
                      SELECT
                      l.partner_id, 
                      inv.company_id, 
                      0 as turnover_180, 
                      SUM(l.debit - l.credit) as turnover_360, 
                      0 as total_turnover,
                      0 as tot_due
                      FROM account_move_line l
                      LEFT JOIN account_move inv ON l.move_id = inv.id
                      LEFT JOIN account_account acc ON l.account_id = acc.id
                      WHERE
                      l.partner_id IN %(partner_ids)s
                      AND l.date >= %(date_from_360)s
                      AND l.date <= %(date_to)s
                      AND l.company_id IN %(company_ids)s
                      AND inv.state = 'posted'
                      AND acc.account_type in ('asset_receivable')
                      AND inv.move_type IN ('out_refund', 'out_invoice')
                      GROUP BY l.partner_id, inv.company_id 
                  union all
                      SELECT
                      l.partner_id, 
                      inv.company_id, 
                      0 as turnover_180, 
                      0 as turnover_360, 
                      SUM(l.debit - l.credit) as total_turnover,
                      0 as tot_due
                      FROM account_move_line l
                      LEFT JOIN account_move inv ON l.move_id = inv.id
                      LEFT JOIN account_account acc ON l.account_id = acc.id
                      WHERE
                      l.partner_id IN %(partner_ids)s
                      AND l.date <= %(date_to)s
                      AND l.company_id IN %(company_ids)s
                      AND inv.state = 'posted'
                      AND acc.account_type in ('asset_receivable')
                      AND inv.move_type IN ('out_refund', 'out_invoice')
                      GROUP BY l.partner_id, inv.company_id
                  union all
                      SELECT
                      l.partner_id, 
                      inv.company_id, 
                      0 as turnover_180, 
                      0 as turnover_360, 
                      0 as total_turnover,
                      SUM(l.debit - l.credit) as tot_due
                      FROM account_move_line l
                      LEFT JOIN account_move inv ON l.move_id = inv.id
                      LEFT JOIN account_account acc ON l.account_id = acc.id
                      WHERE
                      l.partner_id IN %(partner_ids)s
                      AND l.company_id IN %(company_ids)s
                      AND inv.state = 'posted'
                      AND acc.account_type in ('asset_receivable')
                      GROUP BY l.partner_id, inv.company_id)  
                  AS turnover_total_sub GROUP BY partner_id, company_id
                  """
            date_from_180 = Datetime.today() - relativedelta(days=180)
            date_from_360 = Datetime.today() - relativedelta(days=360)
            date_to = Datetime.today()
            params = {
                'partner_ids': tuple(customer.ids),
                'company_ids': tuple(self.env.companies.ids),
                'date_from_180':date_from_180,
                'date_from_360':date_from_360,
                'date_to':date_to,
            }
            self.env.cr.execute(query, params)
            for record in self.env.cr.dictfetchall():
                evaluation_line = self.env['customer.evaluation.lines'].search([('partner_id', '=', record['partner_id']), ('company_id', '=',record['company_id'])])
                if record['turnover_360'] or record['turnover_180'] or record['total_turnover'] or record['tot_due']:
                    if not evaluation_line:
                        self.env['customer.evaluation.lines'].create({'partner_id':record['partner_id'],
                                                                      'company_id':record['company_id'],
                                                                      'turnover_360_days':record['turnover_360'],
                                                                      'turnover_180_days':record['turnover_180'],
                                                                      'total_turnover':record['total_turnover'],
                                                                      'total_due':record['tot_due']})
                    else:
                        evaluation_line.turnover_360_days = record['turnover_360']
                        evaluation_line.turnover_180_days = record['turnover_180']
                        evaluation_line.total_turnover = record['total_turnover']
                        evaluation_line.total_due = record['tot_due']