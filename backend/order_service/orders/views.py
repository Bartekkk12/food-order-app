from rest_framework import viewsets, permissions

from .models import Product, Restaurant
from .serializers import RestaurantSerializer, ProductSerializer


# Create your views here.


class RestaurantViewSet(viewsets.ModelViewSet):
    """API endpoint that allows restaurants to be viewed or edited."""

    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint that allows product to be viewed or edited."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
