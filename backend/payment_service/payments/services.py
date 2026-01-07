import time


def process_payment(order_id, total_price):
    print(f"[x] Processing payment for order {order_id}")
    time.sleep(3)
    print(f"[✓] Payment for order {order_id} succeed.")
