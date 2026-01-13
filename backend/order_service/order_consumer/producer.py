import pika
import json


def send_payment_message(order_id, total_price):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq"))
        channel = connection.channel()
        channel.queue_declare(queue="payment_queue")

        message = {
            "order_id": order_id,
            "total_price": float(total_price)
        }
        channel.basic_publish(
            exchange='',
            routing_key="payment_queue",
            body=json.dumps(message)
        )
        print(f"[+] Sent message to RabbitMQ: {message}")

        connection.close()
    except Exception as e:
        print(f"[!] Error RabbitMQ: {e}")
