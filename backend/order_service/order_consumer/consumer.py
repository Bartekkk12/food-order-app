import os
import django
import pika
import json

from orders.models import Order

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "order_service.settings")
django.setup()

rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
params = pika.URLParameters(rabbitmq_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="payment_success")


def callback(ch, method, properties, body):
    data = json.loads(body)
    order_id = data.get("order_id")
    try:
        order = Order.objects.get(id=order_id)
        order.status = 'paid'
        order.save()
        print(f"Order {order_id} marked as paid")
    except Order.DoesNotExist:
        print(f"Order {order_id} does not exist")


channel.basic_consume(queue="payment_success", on_message_callback=callback, auto_ack=True)
print("Waiting for payment messages...")
channel.start_consuming()
