from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    # Address paths
    path('addresses/', AddressList.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetail.as_view(), name='address-detail'),

    # User paths
    path('users/', UserList.as_view(), name='user-list'),

    # Auth paths
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/logout/', LogoutUserView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/register/', RegisterUserView.as_view(), name='register'),

    # Restaurant paths
    path('restaurants/', RestaurantList.as_view(), name='restaurant-list'),
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('restaurants/<slug:slug>/', RestaurantDetailBySlug.as_view(), name='restaurant-detail-slug'),

    # Product paths
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('products/<slug:restaurant_slug>/<slug:product_slug>/', ProductDetailBySlug.as_view(), name='product-detail-slug')

]
