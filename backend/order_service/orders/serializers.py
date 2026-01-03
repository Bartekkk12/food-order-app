from rest_framework import serializers

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404

from .models import *


# ------------------ Address ------------------
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'city', 'zip_code', 'street', 'house_number', 'apartment_number']
        read_only_fields = ['id']


# ------------------ User ------------------
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
            raise serializers.ValidationError('User with this email already exists')
        return value

    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({"password_confirm": "Passwords must match."})

        try:
            validate_password(password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

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

        if not email or not password:
            raise serializers.ValidationError({'non_field_errors': 'Both email and password are required'})

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError({'non_field_errors': 'Invalid email or password'})
        if not user.is_active:
            raise serializers.ValidationError({'non_field_errors': 'Your account is disabled'})

        attrs['user'] = user
        return attrs


# ------------------ RESTAURANTS ------------------
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


# ------------------ PRODUCTS ------------------
class ProductSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'restaurant', 'restaurant_name', 'slug']
        read_only_fields = ['id', 'slug', 'restaurant_name']


    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price cannot be negative')
        return value


# ------------------ ORDERS ------------------
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'order', 'quantity']
        read_only_fields = ['id']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price']
        read_only_fields = ['id', 'user', 'total_price']


class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    items = CreateOrderItemSerializer(many=True)

    def validate(self, data):
        restaurant = get_object_or_404(Restaurant, id=data['restaurant_id'])

        product_ids = [item['product_id'] for item in data['items']]
        products = Product.objects.filter(id__in=product_ids)
        products_dict = {p.id: p for p in products}

        for item in data['items']:
            product = products_dict.get(item['product_id'])
            if not product:
                raise serializers.ValidationError(f"Product with id {item['product_id']} does not exist")
            if product.restaurant_id != restaurant.id:
                raise serializers.ValidationError(f"All products must belong to restaurant '{restaurant.name}'")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        restaurant = get_object_or_404(Restaurant, id=validated_data['restaurant_id'])
        items_data = validated_data['items']

        product_ids = [item['product_id'] for item in items_data]
        products = Product.objects.filter(id__in=product_ids)
        products_dict = {p.id: p for p in products}

        order = Order.objects.create(user=user, restaurant=restaurant, total_price=0)
        total_price = 0

        order_items = []
        for item in items_data:
            product = products_dict[item['product_id']]
            order_item = OrderItem(order=order, product=product, quantity=item['quantity'], price=product.price)
            order_items.append(order_item)
            total_price += product.price * item['quantity']

        OrderItem.objects.bulk_create(order_items)

        order.total_price = total_price
        order.save(update_fields=['total_price'])
        return order
