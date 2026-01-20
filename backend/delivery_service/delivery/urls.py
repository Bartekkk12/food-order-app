from django.urls import path
from .views import *

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('deliveries/', DeliveryListView.as_view(), name='delivery-list'),
    path('deliveries/<int:pk>/', DeliveryDetailView.as_view(), name='delivery-detail'),
    path('deliveries/<int:pk>/status/', UpdateDeliveryStatusView.as_view(), name='delivery-status'),
    path('deliveries/order/<int:order_id>/', DeliveryByOrderView.as_view(), name='delivery-by-order'),
]
