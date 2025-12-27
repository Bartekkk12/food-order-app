from django.urls import path

from .views import *

urlpatterns = [
    path('addresses/', AddressList.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetail.as_view(), name='address-detail'),

    path('users/', UserList.as_view(), name='user-list'),

    path('restaurants/', RestaurantList.as_view(), name='restaurant-list'),
    path('restaurants/<int:pk>/', RestaurantDetail.as_view(), name='restaurant-detail'),
    path('restaurants/<slug:slug>/', RestaurantDetailBySlug.as_view(), name='restaurant-detail-slug'),

    path('products/', ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
]
