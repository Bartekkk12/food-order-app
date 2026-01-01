from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.shortcuts import get_object_or_404

from .models import *
from .serializers import *


# Create your views here.


class UserAddressList(APIView):
    """List all user addresses, or create a new address."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = UserAddress.objects.filter(user=request.user)
        serializer = UserAddressSerializer(addresses, many=True)

        return Response(serializer.data)

    def post(self, request):
        serializer = CreateUserAddressSerializer(data=request.data)

        if serializer.is_valid():
            address = serializer.save()
            user_address = UserAddress.objects.create(user=request.user, address=address)
            user_address_serializer = UserAddressSerializer(user_address)

            return Response(user_address_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAddressDetail(APIView):
    """Detail view of a user address."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        user_address = get_object_or_404(UserAddress, pk=pk, user=request.user)
        serializer = AddressSerializer(user_address, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(UserAddressSerializer(user_address).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user_address = get_object_or_404(UserAddress, pk=pk, user=request.user)
        user_address.address.delete()
        user_address.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class AddressDetail(APIView):
    """Retrieve, update or delete a address."""

    def get(self, request, pk):
        address = get_object_or_404(Address, pk=pk)
        serializer = AddressSerializer(address)

        return Response(serializer.data)

    def put(self, request, pk):
        address = get_object_or_404(Address, pk=pk)

        serializer = AddressSerializer(address, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        address = get_object_or_404(Address, pk=pk)
        address.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserList(APIView):
    """List all users"""

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetail(APIView):
    """Retrieve, update or delete a user if is authenticated."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(request.user)
        serializer = UserDetailSerializer(user)

        return Response(serializer.data)

    def put(self, request):
        user = get_object_or_404(request.user)
        serializer = UserDetailSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(APIView):
    """Register a new user."""

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(APIView):
    """Login a user."""

    def post(self, request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'refresh': str(access_token),
            'access': access_token,
            'user': {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'email': user.email,
            }
        }, status=status.HTTP_200_OK)


class LogoutUserView(APIView):
    """Logout a user."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({'message': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({'message': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


class RestaurantList(APIView):
    """List all restaurants, or create a new restaurant."""

    def get(self, request):
        restaurants = Restaurant.objects.all()
        name = request.GET.get('name')
        city = request.GET.get('city')

        if name:
            restaurants = restaurants.filter(name__icontains=name)
        if city:
            restaurants = restaurants.filter(address__city__icontains=city)

        serializer = RestaurantSerializer(restaurants, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestaurantDetail(APIView):
    """Retrieve, update or delete a restaurant."""

    def get(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        serializer = RestaurantSerializer(restaurant)

        return Response(serializer.data)

    def put(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)

        serializer = RestaurantSerializer(restaurant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        restaurant = get_object_or_404(Restaurant, pk=pk)
        restaurant.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RestaurantDetailBySlug(APIView):
    """Retrieve a restaurant by slug"""

    def get(self, request, slug):
        restaurant = get_object_or_404(Restaurant, slug=slug)
        serializer = RestaurantSerializer(restaurant)

        return Response(serializer.data)


class RestaurantAddressList(APIView):
    """List all addresses for a given restaurant, or create a new address."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        restaurant_id = request.query_params.get('restaurant')
        if restaurant_id:
            addresses = RestaurantAddress.objects.filter(restaurant_id=restaurant_id)
        else:
            addresses = RestaurantAddress.objects.all()

        serializer = RestaurantAddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateRestaurantAddressSerializer(data=request.data)
        if serializer.is_valid():
            address = serializer.save()
            restaurant_id = request.data.get('restaurant')
            restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
            restaurant_address = RestaurantAddress.objects.create(restaurant=restaurant, address=address)
            return Response(RestaurantAddressSerializer(restaurant_address).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RestaurantAddressDetail(APIView):
    """Detail view of a user address."""

    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        restaurant_address = get_object_or_404(RestaurantAddress, pk=pk)
        serializer = AddressSerializer(restaurant_address.address, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(RestaurantAddressSerializer(restaurant_address).data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        restaurant_address = get_object_or_404(RestaurantAddress, pk=pk)
        restaurant_address.address.delete()
        restaurant_address.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RestaurantProductList(APIView):
    """List all restaurant products"""

    def get(self, request, slug):
        restaurant = get_object_or_404(Restaurant, slug=slug)
        products = Product.objects.filter(restaurant=restaurant)
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductList(APIView):
    """List all products, or create a new product."""

    def get(self, request):
        products = Product.objects.all()

        restaurant_id = request.GET.get('restaurant')
        if restaurant_id:
            products = products.filter(restaurant_id=restaurant_id)

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetail(APIView):
    """Retrieve, update or delete a product."""

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)

        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductDetailBySlug(APIView):
    """Retrieve a product by slug"""

    def get(self, request, restaurant_slug, product_slug):
        product = get_object_or_404(Product, slug=product_slug, restaurant__slug=restaurant_slug)
        serializer = ProductSerializer(product)

        return Response(serializer.data)
