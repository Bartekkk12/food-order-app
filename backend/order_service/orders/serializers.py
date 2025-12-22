from rest_framework import serializers

from .models import User, Product, Restaurant


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'surname', 'email', 'phone_number', 'address']


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['name', 'address']


class ProductSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Product
        fields = ['name', 'price', 'restaurant', 'restaurant_name']
