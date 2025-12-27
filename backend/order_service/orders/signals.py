from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from decimal import Decimal
from .models import OrderItem


@receiver(post_save, sender=OrderItem)
@receiver(post_delete, sender=OrderItem)
def update_order_total(sender, instance, **kwargs):
    total = sum(Decimal(item.get_total_price()) for item in instance.order.products.all())
    instance.order.total_price = total
    instance.order.save()
