import os
import django
import pika
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'order_service.settings')

django.setup()

from orders.models import Order


def handle_payment_success(data):
    """Handle payment_success messages"""
    order_id = data.get("order_id")
    print(f"[Payment] Processing order ID: {order_id}")

    try:
        order = Order.objects.get(id=order_id)
        print(f"[Payment] Order found: {order.id} with current status: {order.status}")

        order.status = 'paid'
        order.save()
        print(f"[Payment] Order {order_id} updated successfully to status: paid")
    except Order.DoesNotExist:
        print(f"[Payment] Order {order_id} does not exist")
    except Exception as e:
        print(f"[Payment] Unexpected error: {e}")


def handle_delivery_status(data):
    """Handle delivery_status messages"""
    order_id = data.get("order_id")
    delivery_status = data.get("status")
    distance_km = data.get("distance_km")
    
    print(f"[Delivery] Processing order ID: {order_id}, status: {delivery_status}")
    
    try:
        order = Order.objects.get(id=order_id)
        print(f"[Delivery] Order found: {order.id} with current status: {order.status}")
        
        order.status = delivery_status
        order.save()
        print(f"[Delivery] Order {order_id} updated to status: {delivery_status}")
        
        if distance_km:
            print(f"[Delivery] Distance to customer: {distance_km} km")
            
    except Order.DoesNotExist:
        print(f"[Delivery] Order {order_id} does not exist")
    except Exception as e:
        print(f"[Delivery] Unexpected error: {e}")


def callback_payment(ch, method, properties, body):
    """Callback for payment_success queue"""
    print(f"[Payment] Received message: {body}")
    try:
        data = json.loads(body)
        handle_payment_success(data)
    except json.JSONDecodeError as e:
        print(f"[Payment] Failed to parse JSON: {e}")


def callback_delivery(ch, method, properties, body):
    """Callback for delivery_status queue"""
    print(f"[Delivery] Received message: {body}")
    try:
        data = json.loads(body)
        handle_delivery_status(data)
    except json.JSONDecodeError as e:
        print(f"[Delivery] Failed to parse JSON: {e}")


def start_consumer():
    """Start consuming from both queues"""
    rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    params = pika.URLParameters(rabbitmq_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    # Declare queues
    channel.queue_declare(queue="payment_success")
    channel.queue_declare(queue="delivery_status", durable=True)

    print("[*] Waiting for messages on 'payment_success' and 'delivery_status'...")
    
    # Consume from both queues
    channel.basic_consume(
        queue="payment_success",
        on_message_callback=callback_payment,
        auto_ack=True
    )
    
    channel.basic_consume(
        queue="delivery_status",
        on_message_callback=callback_delivery,
        auto_ack=True
    )
    
    channel.start_consuming()


if __name__ == "__main__":
    print("[*] Starting Order Service Consumer...")
    
    while True:
        try:
            start_consumer()
        except Exception as e:
            print(f"[!] Consumer error: {e}")
            print("[*] Retrying in 5 seconds...")
            import time
            time.sleep(5)