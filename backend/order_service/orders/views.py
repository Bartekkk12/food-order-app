from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import *
from .serializers import *
from .filters import RestaurantFilter


# Create your views here.


class UserAddressList(generics.ListCreateAPIView):
    """List all addresses for the authenticated user or create a new address."""

    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUserAddressSerializer
        return UserAddressSerializer

    def perform_create(self, serializer):
        address = serializer.save()
        UserAddress.objects.create(user=self.request.user, address=address)


class UserAddressDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user address."""

    serializer_class = UserAddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserAddress.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.address.delete()
        instance.delete()


class UserList(generics.ListAPIView):
    """List all users (admin only)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetail(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class RegisterUserView(APIView):
    """Register a new user."""

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            return Response({'message': 'User registered successfully.'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginUserView(TokenObtainPairView):
    """Authenticate a user and return access and refresh tokens."""

    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        return Response({
            'refresh': str(refresh),
            'access': access,
            'user': {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'email': user.email,
            }
        }, status=status.HTTP_200_OK)


class LogoutUserView(APIView):
    """Logout the authenticated user by blacklisting the refresh token."""

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


class RestaurantList(generics.ListCreateAPIView):
    """List all restaurants or create a new restaurant."""

    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = RestaurantFilter
    permission_classes = [IsAuthenticatedOrReadOnly]


class RestaurantDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a restaurant."""

    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RestaurantAddressList(generics.ListCreateAPIView):
    """List all addresses for a restaurant or create a new address."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        restaurant_id = self.request.query_params.get('restaurant')
        queryset = RestaurantAddress.objects.all()

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateRestaurantAddressSerializer
        return RestaurantAddressSerializer

    def perform_create(self, serializer):
        address = serializer.save()
        restaurant_id = self.request.data.get('restaurant')
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        RestaurantAddress.objects.create(restaurant=restaurant, address=address)


class RestaurantAddressDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a restaurant address."""

    queryset = RestaurantAddress.objects.all()
    serializer_class = RestaurantAddressSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        address = self.get_object().address
        address_serializer = AddressSerializer(address, data=self.request.data, partial=True)
        address_serializer.is_valid(raise_exception=True)
        address_serializer.save()

    def perform_destroy(self, instance):
        instance.address.delete()
        instance.delete()


class RestaurantProductList(generics.ListAPIView):
    """List all products for a given restaurant."""

    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        restaurant_slug = self.kwargs.get('slug')
        restaurant = get_object_or_404(Restaurant, slug=restaurant_slug)

        return Product.objects.filter(restaurant=restaurant)


class ProductList(generics.ListCreateAPIView):
    """List all products or create a new product."""

    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Product.objects.all()
        restaurant_id = self.request.query_params.get('restaurant')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset


class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a product."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductDetailBySlug(generics.RetrieveAPIView):
    """Retrieve a product by restaurant slug and product slug."""

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        restaurant_slug = self.kwargs.get('restaurant_slug')
        product_slug = self.kwargs.get('product_slug')

        return get_object_or_404(Product, slug=product_slug, restaurant__slug=restaurant_slug)


class UserOrdersList(generics.ListAPIView):
    """List all orders for the authenticated user."""

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CreateOrderView(generics.CreateAPIView):
    """Create a new order."""

    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
