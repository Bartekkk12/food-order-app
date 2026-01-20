import time
import pika
import json


def process_payment(order_id, total_price):
    print(f"[x] Processing payment for order {order_id}")
    time.sleep(3)
    print(f"[✓] Payment for order {order_id} succeeded")

    send_payment_success(order_id)


def send_payment_success(order_id):
    """Send payment success to both order service and delivery service"""
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", port=5672)
    )
    channel = connection.channel()

    # Queue for order service
    channel.queue_declare(queue="payment_success")
    
    # Queue for delivery service
    channel.queue_declare(queue="delivery_queue", durable=True)

    # Message for order service (simple)
    order_message = {
        "order_id": order_id,
        "status": "paid"
    }
    
    channel.basic_publish(
        exchange="",
        routing_key="payment_success",
        body=json.dumps(order_message)
    )
    print(f"[+] Sent payment_success to order service for order {order_id}")
    
    # Message for delivery service (only order_id - delivery will fetch details from order service)
    delivery_message = {
        "order_id": order_id
    }
    
    channel.basic_publish(
        exchange="",
        routing_key="delivery_queue",
        body=json.dumps(delivery_message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )
    print(f"[+] Sent delivery request for order {order_id}")

    connection.close()

