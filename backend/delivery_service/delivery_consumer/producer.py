import pika
import json
import os


def send_delivery_status(order_id, delivery_id, status, distance_km=None):
    """ Send delivery status update to order service """
    try:
        rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
        params = pika.URLParameters(rabbitmq_url)
        
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        # Declare queue
        channel.queue_declare(queue="delivery_status", durable=True)
        
        # Prepare message
        message = {
            "order_id": order_id,
            "delivery_id": delivery_id,
            "status": status,
        }
        
        if distance_km is not None:
            message["distance_km"] = distance_km
        
        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key="delivery_status",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        
        print(f"[+] Sent delivery status to RabbitMQ: {message}")
        
        connection.close()
        
    except Exception as e:
        print(f"[!] Error sending delivery status to RabbitMQ: {e}")
