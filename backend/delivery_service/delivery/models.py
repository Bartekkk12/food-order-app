from django.db import models


class Delivery(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ON_THE_WAY = 'on_the_way'
    STATUS_DELIVERED = 'delivered'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_ON_THE_WAY, 'On the way'),
        (STATUS_DELIVERED, 'Delivered'),
    )

    order_id = models.IntegerField(unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    distance_km = models.FloatField(null=True, blank=True)
    estimated_time = models.DurationField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Delivery for Oder #{self.order_id} - {self.status}'
