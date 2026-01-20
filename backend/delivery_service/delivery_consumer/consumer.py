import os
import django
import pika
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'delivery_service.settings')
django.setup()

from delivery.models import Delivery
from delivery.google_maps import GoogleMapsService
from delivery_consumer.producer import send_delivery_status
from datetime import timedelta


ORDER_SERVICE_URL = os.environ.get('ORDER_SERVICE_URL', 'http://order_service:8000')


def fetch_order_details(order_id):
    """
    Fetch order details from Order Service API
    Returns order with restaurant and user addresses
    """
    try:
        # Fetch order details
        url = f"{ORDER_SERVICE_URL}/api/orders/{order_id}/"
        print(f"[*] Fetching order details from: {url}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        order_data = response.json()
        print(f"[✓] Order data received: {order_data}")
        
        # Extract restaurant and user info
        restaurant_id = order_data.get('restaurant')
        user_id = order_data.get('user')
        
        # Fetch restaurant address
        restaurant_url = f"{ORDER_SERVICE_URL}/api/restaurants/{restaurant_id}/"
        restaurant_response = requests.get(restaurant_url, timeout=10)
        restaurant_response.raise_for_status()
        restaurant_data = restaurant_response.json()
        
        # Get first restaurant address
        restaurant_addresses = restaurant_data.get('addresses', [])
        if not restaurant_addresses:
            print(f"[!] No address found for restaurant {restaurant_id}")
            return None
        
        restaurant_addr = restaurant_addresses[0]['address']
        restaurant_address = format_address(restaurant_addr)
        
        # Fetch user addresses
        user_url = f"{ORDER_SERVICE_URL}/api/users/{user_id}/addresses/"
        user_response = requests.get(user_url, timeout=10)
        user_response.raise_for_status()
        user_addresses = user_response.json()
        
        if not user_addresses:
            print(f"[!] No address found for user {user_id}")
            return None
        
        # Get first user address
        user_addr = user_addresses[0]['address']
        customer_address = format_address(user_addr)
        
        return {
            'order_id': order_id,
            'restaurant_address': restaurant_address,
            'customer_address': customer_address
        }
        
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching order details: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"[!] Error parsing order data: {e}")
        return None


def format_address(address_dict):
    """Format address dict into string"""
    parts = [
        address_dict.get('street', ''),
        address_dict.get('house_number', ''),
        address_dict.get('city', ''),
        address_dict.get('zip_code', ''),
        address_dict.get('country', 'Poland')
    ]
    return ', '.join(filter(None, parts))


def callback(ch, method, properties, body):
    """Process incoming messages from delivery_queue"""
    print(f"[x] Received message: {body}")
    
    try:
        data = json.loads(body)
        order_id = data.get("order_id")
        
        print(f"[*] Processing delivery for order ID: {order_id}")
        
        # Check if delivery already exists
        if Delivery.objects.filter(order_id=order_id).exists():
            print(f"[!] Delivery for order {order_id} already exists. Skipping...")
            return
        
        # Fetch order details from Order Service
        order_details = fetch_order_details(order_id)
        
        if not order_details:
            print(f"[!] Failed to fetch order details for order {order_id}")
            return
        
        restaurant_address = order_details['restaurant_address']
        customer_address = order_details['customer_address']
        
        print(f"[*] Restaurant: {restaurant_address}")
        print(f"[*] Customer: {customer_address}")
        
        # Calculate distance using Google Maps API
        maps_service = GoogleMapsService()
        route_data = maps_service.calculate_distance(
            origin=restaurant_address,
            destination=customer_address
        )
        
        # Create delivery record
        delivery = Delivery.objects.create(
            order_id=order_id,
            start_location=restaurant_address,
            end_location=customer_address,
            distance_km=route_data['distance_km'],
            estimated_time=timedelta(seconds=route_data['duration_seconds']),
            status=Delivery.STATUS_PENDING
        )
        
        print(f"[✓] Delivery created: ID={delivery.id}, Order={order_id}")
        print(f"    Route: {route_data['distance_km']} km, ~{route_data['duration_seconds']//60} min")
        
        # Update delivery status to "on the way"
        delivery.status = Delivery.STATUS_ON_THE_WAY
        delivery.save()
        print(f"[✓] Delivery {delivery.id} status updated to: {Delivery.STATUS_ON_THE_WAY}")
        
        # Send delivery status to order service
        send_delivery_status(
            order_id=order_id,
            delivery_id=delivery.id,
            status='in_progress',  # Order service status
            distance_km=route_data['distance_km']
        )
        
    except json.JSONDecodeError as e:
        print(f"[!] Failed to parse message JSON: {e}")
    except Exception as e:
        print(f"[!] Error processing delivery: {e}")
        import traceback
        traceback.print_exc()


def start_consumer():
    """Start listening to the delivery_queue"""
    print("[*] Connecting to RabbitMQ...")
    
    rabbitmq_url = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
    params = pika.URLParameters(rabbitmq_url)
    
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    
    # Declare queue
    channel.queue_declare(queue="delivery_queue", durable=True)
    
    print("[*] Waiting for delivery requests on 'delivery_queue'...")
    
    channel.basic_consume(
        queue="delivery_queue",
        on_message_callback=callback,
        auto_ack=True
    )
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n[*] Stopping consumer...")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    print("[*] Starting Delivery Service Consumer...")
    
    while True:
        try:
            start_consumer()
        except Exception as e:
            print(f"[!] Consumer error: {e}")
            print("[*] Retrying in 5 seconds...")
            import time
            time.sleep(5)
