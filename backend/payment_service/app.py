from payments.processor import start_consumer
import time

if __name__ == "__main__":
    print("Starting the RabbitMQ Consumer...")
    while True:
        try:
            start_consumer()
        except Exception as e:
            print(f"[!] Starting the consumer ended with an error: {e}")
            print("[*] Trying again in 5 seconds...")
            time.sleep(5)
