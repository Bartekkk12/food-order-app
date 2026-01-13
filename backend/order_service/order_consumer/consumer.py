import os
import django
import pika
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

django.setup()

from orders.models import Order


def callback(ch, method, properties, body):
    print("Received message:", body)
    data = json.loads(body)

    order_id = data.get("order_id")
    print(f"Processing order ID: {order_id}")

    try:
        order = Order.objects.get(id=order_id)
        print(f"Order found: {order.id} with current status: {order.status}")

        order.status = 'paid'
        order.save()
        print(f"Order {order_id} updated successfully to status: paid")
    except Order.DoesNotExist:
        print(f"Order {order_id} does not exist")
    except Exception as e:
        print(f"Unexpected error: {e}")


rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
params = pika.URLParameters(rabbitmq_url)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="payment_success")

print("Waiting for messages...")
channel.basic_consume(queue="payment_success", on_message_callback=callback, auto_ack=True)
channel.start_consuming()