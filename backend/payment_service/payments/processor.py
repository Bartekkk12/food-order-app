import pika
import json

from payments.services import process_payment


def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        order_id = message["order_id"]
        total_price = message["total_price"]

        print(f"[x] Received message: {message}")
        process_payment(order_id, total_price)

    except Exception as e:
        print(f"[!] Message processing error: {e}")


def start_consumer():
    print("[*] Connecting to RabbitMQ...")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq", port=5672)
    )
    channel = connection.channel()

    channel.queue_declare(queue="payment_queue")

    print("[*] Listening on 'payment_queue'...")

    channel.basic_consume(
        queue="payment_queue",
        on_message_callback=callback,
        auto_ack=True
    )

    channel.start_consuming()
