from django.urls import include, path
from rest_framework import routers

from .views import UserViewSet, RestaurantViewSet, ProductViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)  # Returns users list
router.register(r'restaurants', RestaurantViewSet)  # Returns restaurants list
router.register(r'products', ProductViewSet)  # Returns products list

urlpatterns = [
    path('', include(router.urls)),
]
