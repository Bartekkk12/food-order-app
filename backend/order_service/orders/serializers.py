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


class RestaurantSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ['id', 'name', 'slug', 'addresses']
        read_only_fields = ['id', 'slug']

    def get_addresses(self, obj):
        request = self.context.get('request')
        city = request.query_params.get('city') if request else None

        qs = obj.restaurantaddress_set.all()
        if city:
            qs = qs.filter(address__city__iexact=city)
        return RestaurantAddressSerializer(qs, many=True).data


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
        fields = ['product', 'quantity', 'price']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity cannot be negative')
        return value


class OrderSerializer(serializers.ModelSerializer):
    products = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'restaurant', 'products', 'total_price', 'status', 'created_at']
        read_only_fields = fields


class CreateOrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    restaurant_id = serializers.IntegerField()
    items = CreateOrderItemSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        restaurant = get_object_or_404(Restaurant, id=validated_data['restaurant_id'])

        order = Order.objects.create(
            user=user,
            restaurant=restaurant,
            total_price=0
        )

        total_price = 0
        order_items = []

        for item in validated_data['items']:
            product = Product.objects.get(id=item['product_id'])
            quantity = item['quantity']
            total_price += product.price * quantity

            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            ))

        OrderItem.objects.bulk_create(order_items)

        order.total_price = total_price
        order.save()

        return order
