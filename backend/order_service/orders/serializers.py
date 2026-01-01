from rest_framework import serializers
from rest_framework.validators import ValidationError

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from .models import Address, User, UserAddress, Product, Restaurant, RestaurantAddress


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'city', 'zip_code', 'street', 'house_number', 'apartment_number']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name']
        read_only_fields = ['id']


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'surname', 'email', 'phone_number']
        read_only_fields = ['id']


class UserAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer()

    class Meta:
        model = UserAddress
        fields = ['id', 'address']


class CreateUserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country', 'city', 'zip_code', 'street', 'house_number', 'apartment_number']


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'name', 'surname', 'phone_number']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError('User with this email already exists')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Passwords must match."
            })
        return attrs

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(password=password, **validated_data)
        user.save()

        return user


class LoginUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError({'email': 'Invalid email or password'})
            if not user.is_active:
                raise ValidationError('Your account is disabled')
        else:
            raise ValidationError({'email': 'Both email and password are required'})

        attrs['user'] = user
        return attrs


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


class RestaurantAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = RestaurantAddress
        fields = ['id', 'restaurant', 'restaurant_name', 'address']


class CreateRestaurantAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['country', 'city', 'zip_code', 'street', 'house_number', 'apartment_number']


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
