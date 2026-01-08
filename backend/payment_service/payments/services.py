import time
import pika
import json


def process_payment(order_id, total_price):
    print(f"[x] Processing payment for order {order_id}")
    time.sleep(3)
    print(f"[✓] Payment for order {order_id} succeeded")

    send_payment_success(order_id)


def send_payment_success(order_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", port=5672)
    )
    channel = connection.channel()

    channel.queue_declare(queue="payment_success")

    channel.basic_publish(
        exchange="",
        routing_key="payment_success",
        body=json.dumps({
            "order_id": order_id,
            "status": "paid"
        })
    )

    print(f"[+] Sent payment_success for order {order_id}")
    connection.close()
