from odoo import models

class DeliverySummaryReport(models.AbstractModel):
    _name = 'report.productivity_report.report_delivery_summary_document'
    _description = 'Delivery Summary Report'


    def get_delivery_summary_data(self, invoice):
        """Return a list of dictionaries with delivery info related to the invoice"""
        result = []
        if invoice.invoice_origin:
            sale_orders = self.env['sale.order'].search([('name', 'in', invoice.invoice_origin.split(','))])

            for sale_order in sale_orders:
                result  = self.env['x_alkon.raw.data'].search([('x_record_type', '=', 'Ticket'), ('x_delivery_ref', '=',sale_order.name)])

        return result



    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        delivery_data = {doc.id: self.get_delivery_summary_data(doc) for doc in docs}
        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'delivery_data': delivery_data,
        }
