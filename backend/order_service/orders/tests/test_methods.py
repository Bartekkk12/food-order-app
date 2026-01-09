import json

from orders.models import Order, User
from order_consumer.consumer import callback
from test_views import BaseConfig


class PaymentConsumerTestCase(BaseConfig):
    def setUp(self):
        super().setUp()

        self.order = Order.objects.create(
            user=self.user,
            restaurant=self.restaurant1,
            total_price=100,
            status='created'
        )

    def test_callback_marks_order_paid(self):
        body = json.dumps({
            "order_id": self.order.id,
        }).encode('utf-8')

        callback(
            ch=None,
            method=None,
            properties=None,
            body=body,
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'paid')
