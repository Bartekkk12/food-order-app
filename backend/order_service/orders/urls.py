from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

urlpatterns = [
    # User paths
    path('users/', UserList.as_view(), name='user-list'),
    path('users/addresses/', UserAddressList.as_view(), name='user-address-list'),
    path('users/addresses/<int:pk>/', UserAddressDetail.as_view(), name='user-address-detail'),

    # Auth paths
    path('auth/login/', LoginUserView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('auth/logout/', LogoutUserView.as_view(), name='logout'),
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/me/', UserDetail.as_view(), name='auth-me'),

    # Restaurant paths
    path('restaurants/', RestaurantList.as_view(), name='restaurant-list'),
    path('restaurants/address/', RestaurantAddressList.as_view(), name='restaurant-address-list'),
    path('restaurants/<slug:slug>/products/', RestaurantProductList.as_view(), name='restaurant-product-list'),
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('restaurants/<slug:slug>/', RestaurantDetailBySlug.as_view(), name='restaurant-detail-slug'),
    path('restaurants/<int:pk>/address/', RestaurantAddressDetail.as_view(), name='restaurant-address-detail'),

    # Product paths
    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('products/<slug:restaurant_slug>/<slug:product_slug>/', ProductDetailBySlug.as_view(), name='product-detail-slug'),

]
