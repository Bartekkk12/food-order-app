from rest_framework import viewsets, permissions

from .models import User, Product, Restaurant
from .serializers import UserSerializer, RestaurantSerializer, ProductSerializer


# Create your views here.


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet to list all users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class RestaurantViewSet(viewsets.ModelViewSet):
    """API endpoint that allows restaurants to be viewed or edited."""

    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint that allows product to be viewed or edited."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
