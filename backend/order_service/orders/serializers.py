from rest_framework import serializers
from rest_framework.validators import ValidationError

from .models import Address, User, Product, Restaurant


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'city', 'zip_code', 'street', 'house_number', 'apartment_number']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'surname', 'email', 'phone_number']
        read_only_fields = ['id']


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'name', 'surname', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise ValidationError({'password': 'Passwords do not match'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)
        user.save()

        return user


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'address', 'slug']
        read_only_fields = ['id', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'restaurant', 'restaurant_name', 'slug']
        read_only_fields = ['id', 'slug', 'restaurant_name']

    def validate_price(self, value):
        if value <= 0:
            raise ValidationError('Price cannot be negative')
        return value
