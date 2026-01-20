from rest_framework import serializers
from .models import Delivery


class DeliverySerializer(serializers.ModelSerializer):
    """Serializer for Delivery model"""
    
    class Meta:
        model = Delivery
        fields = [
            'id',
            'order_id',
            'status',
            'start_location',
            'end_location',
            'distance_km',
            'estimated_time',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateDeliverySerializer(serializers.ModelSerializer):
    """Serializer for creating a new delivery"""
    
    class Meta:
        model = Delivery
        fields = ['order_id', 'start_location', 'end_location']
    
    def validate_order_id(self, value):
        """Check if delivery for this order already exists"""
        if Delivery.objects.filter(order_id=value).exists():
            raise serializers.ValidationError(
                f"Delivery for order {value} already exists"
            )
        return value


class UpdateDeliveryStatusSerializer(serializers.ModelSerializer):
    """Serializer for updating delivery status"""
    
    class Meta:
        model = Delivery
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition"""
        valid_statuses = [choice[0] for choice in Delivery.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        return value
