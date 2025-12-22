# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
from werkzeug import urls
from odoo import _, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_skipcash_odoie import const
from odoo.addons.payment_skipcash_odoie.controllers.main import SkipcashController

from decimal import Decimal
from skipcash.schema import PaymentInfo
from skipcash.exceptions import  PaymentValidationError, PaymentInfoError
from skipcash.exceptions import PaymentRetrievalError, PaymentResponseError
from skipcash.api_resources import Payment

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _get_specific_processing_values(self, processing_values):
        """ Override of payment to redirect pending token-flow transactions.

        If the financial institution insists on 3-D Secure authentication, this
        override will redirect the user to the provided authorization page.

        Note: `self.ensure_one()`
        """
        res = super()._get_specific_processing_values(processing_values)
        if self._skipcash_is_authorization_pending():
            res['redirect_form_html'] = self.env['ir.qweb']._render(
                self.provider_id.redirect_form_view_id.id,
                {'api_url': self.provider_reference},
            )
        return res

    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return skipcash-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'skipcash':
            return res

        # Initiate the payment and retrieve the payment link data.
        base_url = self.provider_id.get_base_url()
        first_name, last_name = payment_utils.split_partner_name(self.partner_name)
        skipcash = self.provider_id.skipcash_get()
        payment_info = PaymentInfo(
            key_id=skipcash.key_id,
            amount=Decimal(str(self.amount)),
            first_name=first_name,
            last_name=last_name,
            phone=self.partner_phone,
            email=self.partner_email,
            street=self.partner_address[:50],
            city=self.partner_city[:50],
            transaction_id=self.reference,
            # custom_fields={'Custom1': 'value1', 'Custom2': 'value2'}  # Optional
        )
        try:
            payment = Payment(skipcash)
            response = payment.create_payment(payment_info)
            rendering_values = {
                'api_url': response.pay_url,
            }
            return rendering_values
        except PaymentInfoError as e:
            print(f"Error: {e}")
        except PaymentValidationError as e:
            print(f"Validation Error: {e}")
        except PaymentResponseError as e:
            print(f"Response Error: {e}")

    def _send_payment_request(self):
        """ Override of payment to send a payment request to skipcash.

        Note: self.ensure_one()

        :return: None
        :raise UserError: If the transaction is not linked to a token.
        """
        super()._send_payment_request()
        if self.provider_code != 'skipcash':
            return

        # Prepare the payment request to skipcash.
        if not self.token_id:
            raise UserError("skipcash: " + _("The transaction is not linked to a token."))

        first_name, last_name = payment_utils.split_partner_name(self.partner_name)
        base_url = self.provider_id.get_base_url()
        data = {
            'token': self.token_id.provider_ref,
            'email': self.token_id.skipcash_customer_email,
            'amount': self.amount,
            'currency': self.currency_id.name,
            'country': self.company_id.country_id.code,
            'tx_ref': self.reference,
            'first_name': first_name,
            'last_name': last_name,
            'ip': payment_utils.get_customer_ip_address(),
            'redirect_url': urls.url_join(base_url, SkipcashController._auth_return_url),
        }

        # Make the payment request to Flutterwave.
        response_content = self.provider_id._skipcash_make_request(
            'tokenized-charges', payload=data
        )

        # Handle the payment request response.
        _logger.info(
            "payment request response for transaction with reference %s:\n%s",
            self.reference, pprint.pformat(response_content)
        )
        self._process('skipcash', response_content['data'])

    def _search_by_reference(self, provider_code, payment_data):
        """ Override of payment to find the transaction based on skipcash data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict payment_data: The payment data sent by the provider.
        :return: The transaction if found.
        :rtype: recordset of `payment.transaction`
        """
        if provider_code != 'skipcash':
            return super()._search_by_reference(provider_code, payment_data)

        reference = payment_data.get('transId')
        if not reference:
            _logger.warning("Received data with missing reference.")
            return self

        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'skipcash')])
        if not tx:
            _logger.warning("No transaction found matching reference %s.", reference)
        return tx

    def _apply_updates(self, payment_data):
        """ Override of payment to process the transaction based on skipcash data.

        Note: self.ensure_one()

        :param dict payment_data: The notification data sent by the provider.
        :return: None
        """
        super()._apply_updates(payment_data)
        if self.provider_code != 'skipcash':
            return

        skipcash = self.provider_id.skipcash_get()
        payment = Payment(skipcash)
        try:
            verified_data = payment.get_payment(payment_data.get('id'))
        except PaymentRetrievalError as e:
            _logger.error(e)
            return # Should probably return or handle error better, but following original logic flow somewhat

        # Update the provider reference.
        self.provider_reference = verified_data.id

        # Update payment method.
        payment_method_type = verified_data.card_type
        if payment_method_type:
            payment_method_type = verified_data.card_type.lower()
        payment_method = self.env['payment.method']._get_from_code(
            payment_method_type, mapping=const.PAYMENT_METHODS_MAPPING
        )
        self.payment_method_id = payment_method or self.payment_method_id

        # Update the payment state.
        payment_status = verified_data.status.lower()
        if payment_status in const.PAYMENT_STATUS_MAPPING['pending']:
            auth_url = payment_data.get('meta', {}).get('authorization', {}).get('redirect')
            if auth_url:
                # will be set back to the actual value after moving away from pending
                self.provider_reference = auth_url
            self._set_pending()
        elif payment_status in const.PAYMENT_STATUS_MAPPING['done']:
            self._set_done()
        elif payment_status in const.PAYMENT_STATUS_MAPPING['cancel']:
            self._set_canceled()
        elif payment_status in const.PAYMENT_STATUS_MAPPING['error']:
            self._set_error(_(
                "An error occurred during the processing of your payment (status %s). Please try "
                "again.", payment_status
            ))
        else:
            _logger.warning(
                "Received data with invalid payment status (%s) for transaction with reference %s.",
                payment_status, self.reference
            )
            self._set_error("skipcash: " + _("Unknown payment status: %s", payment_status))

    def _extract_token_values(self, payment_data):
        """ Create a new token based on the notification data.

        Note: self.ensure_one()

        :param dict payment_data: The notification data sent by the provider.
        :return: None
        """
        if self.provider_code != 'skipcash':
            return super()._extract_token_values(payment_data)

        return {
            'provider_id': self.provider_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_details': payment_data['card']['last_4digits'],
            'partner_id': self.partner_id.id,
            'provider_ref': payment_data['card']['token'],
            'skipcash_customer_email': payment_data['customer']['email'],
        }

    def _skipcash_is_authorization_pending(self):
        return self.filtered_domain([
            ('provider_code', '=', 'skipcash'),
            ('operation', '=', 'online_token'),
            ('state', '=', 'pending'),
            ('provider_reference', 'ilike', 'https'),
        ])
