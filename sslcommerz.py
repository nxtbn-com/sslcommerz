import json
from sslcommerz_lib import SSLCOMMERZ
from decimal import Decimal
from typing import Optional, Any, Dict
from nxtbn.order.models import Order, OrderLineItem
from nxtbn.payment.base import PaymentPlugin, PaymentResponse
from rest_framework import serializers, status
from rest_framework.response import Response
from nxtbn.payment.models import Payment
from nxtbn.payment.payment_manager import PaymentManager
from nxtbn.settings import get_env_var
from datetime import datetime
from nxtbn.payment import PaymentMethod, PaymentStatus


# SSLCommerz settings
SSLCOMMERZ_STORE_ID = get_env_var("SSLCOMMERZ_STORE_ID")
SSLCOMMERZ_STORE_PASSWORD = get_env_var("SSLCOMMERZ_STORE_PASSWORD")

SSLCOMMERZ_INIT_URL = get_env_var("SSLCOMMERZ_INIT_URL")
SSLCOMMERZ_VALIDATE_URL = get_env_var("SSLCOMMERZ_VALIDATE_URL")
SSLCOMMERZ_SANDBOX = get_env_var("SSLCOMMERZ_SANDBOX")

SSLCommerz_SUCCESS_URL = get_env_var('SSLCommerz_SUCCESS_URL', 'http://127.0.0.1:8000/payment/storefront/api/webhook-view/sslcommerz/')
SSLCommerz_CANCEL_URL = get_env_var('SSLCommerz_CANCEL_URL', 'http://localhost:3000/cart')


class SSLCommerzSerializer(serializers.Serializer):
    pass

class SSLCommerzPaymentLinkGateway(PaymentPlugin):

    gateway_name = 'sslcommerz'

    def authorize(self, amount: Decimal, order_id: str, **kwargs):
        """Authorize a payment with SSLCommerz."""
        pass  # Implement authorization logic for SSLCommerz

    def capture(self, amount: Decimal, order_id: str, **kwargs):
        """Capture a previously authorized payment with SSLCommerz."""
        pass  # Implement capture logic for SSLCommerz

    def cancel(self, order_id: str, **kwargs):
        """Cancel an authorized payment with SSLCommerz."""
        pass  # Implement cancelation logic for SSLCommerz

    def refund(self, payment_id: str, amount: str, **kwargs):
        """Refund a captured payment with SSLCommerz."""
        pass

    def partial_refund(self, amount: Decimal, order_id: str, **kwargs):
       pass # Implement partial refund logic for SSLCommerz

    def normalize_response(self, raw_response: Any) -> PaymentResponse:
        """Normalize the SSLCommerz response to a consistent PaymentResponse."""
        pass  # Implement normalization logic for SSLCommerz response

    def special_serializer(self):
        """Return a serializer for handling client-side payloads in API views."""
        return SSLCommerzSerializer()
        # Implement serializer for SSLCommerz

    def public_keys(self) -> Dict[str, Any]:
        """
        Retrieve public keys and non-sensitive information required for secure communication and client-side operations with SSLCommerz.
        """
        pass  # Implement method to retrieve public keys for SSLCommerz

    def payment_url_with_meta(self, order_alias: str, **kwargs) -> Dict[str, Any]:
        """
        Get payment URL and additional metadata based on the order ID for SSLCommerz.
        """
        order = Order.objects.filter(alias=order_alias).first()
        order_items = order.line_items.all()

        categories = set()
        product_name = []
        for line_item in order.line_items.all():
            product_variant = line_item.variant
            product = product_variant.product

            prod_name = product.name
            product_name.append(prod_name)

            category = product.category
            categories.add(category)


        product_category = []
        for category in categories:
            product_category.append(category.name)

        line_items = []
        item_quantity = 0

        for item in order_items:

            item_quantity += item.quantity

            line_items.append({
            'price_data': {
                'currency': self.get_currency_code(),
                'unit_amount': self.get_unit_amount(item.price_per_unit),
                'product_data': {
                    'name': item.variant.name,
                    'description': 'Dummy Description',
                    'images': ['https://example.com/t-shirt.png'],
            },
            },
            'quantity': item.quantity,
        })  

        try:
            data = { 'store_id': SSLCOMMERZ_STORE_ID, 'store_pass': SSLCOMMERZ_STORE_PASSWORD, 'issandbox': True }
            sslcommerz = SSLCOMMERZ(data)

            post_body = {}
            post_body['total_amount'] = order.total_price
            post_body['currency'] = self.get_currency_code().upper()
            post_body['tran_id'] = order.alias
            post_body['success_url'] = SSLCommerz_SUCCESS_URL
            post_body['fail_url'] = SSLCommerz_CANCEL_URL
            post_body['cancel_url'] = SSLCommerz_CANCEL_URL
            post_body['emi_option'] = 0
            post_body['cus_name'] = order.shipping_address.user
            post_body['cus_email'] = order.shipping_address.email_address
            post_body['cus_phone'] = order.shipping_address.phone_number
            post_body['cus_add1'] =  order.shipping_address.street_address
            post_body['cus_city'] = order.shipping_address.city
            post_body['cus_country'] = order.shipping_address.country
            post_body['shipping_method'] = 'NO'
            post_body['multi_card_name'] = ""
            post_body['num_of_item'] = item_quantity
            post_body['product_name'] = product_name
            post_body['product_amount'] = order.total_price
            post_body['product_category'] = product_category
            post_body['product_profile'] = order_items
            post_body['cart'] = line_items


            checkout_session = sslcommerz.createSession(post_body)

            return {
                "url": checkout_session['GatewayPageURL'],
                "order_alias": order_alias
            }

        except Exception as e:
            return str(e)

    def handle_webhook_event(self, request_data: Dict[str, Any], payment_plugin_id: str):
        """
        Handle a webhook event received from SSLCommerz.
        """
        request = request_data

        data = { 'store_id': SSLCOMMERZ_STORE_ID, 'store_pass': SSLCOMMERZ_STORE_PASSWORD, 'issandbox': SSLCOMMERZ_SANDBOX}
        sslcz = SSLCOMMERZ(data)

        if request.method == 'POST':
            post_data = request.POST

            val_id = post_data['val_id']


            if sslcz.hash_validate_ipn(post_data):
                response = sslcz.validationTransactionOrder(val_id)

                order_alias = post_data["tran_id"]

                order = Order.objects.get(alias=order_alias)

                payment_payload = {
                    "order_alias": order_alias,
                    "payment_amount": post_data['amount'],
                    "gateway_response_raw": post_data,
                    "paid_at": datetime.strptime(str(post_data['tran_date']), "%Y-%m-%d %H:%M:%S"),
                    "transaction_id": post_data['bank_tran_id'],
                    "payment_method": PaymentMethod.CREDIT_CARD,
                    "payment_status": PaymentStatus.CAPTURED,
                    "order": order.pk,
                    "payment_plugin_id": payment_plugin_id,
                    "gateway_name": self.gateway_name,
                }

                self.create_payment_instance(payment_payload)

            else:
                raise("Hash validation failed")

        return Response(status=status.HTTP_200_OK)