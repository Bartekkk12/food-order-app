from rest_framework import serializers

from .models import Product, Restaurant


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['name', 'address']


class ProductSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(
        source='restaurant.restaurant_name',
        read_only=True
    )

    class Meta:
        model = Product
        fields = ['name', 'price', 'restaurant', 'restaurant_name']
