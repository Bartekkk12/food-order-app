from django.urls import path

from .views import AddressList, AddressDetail, UserList

urlpatterns = [
    path('addresses/', AddressList.as_view()),
    path('address/<int:pk>/', AddressDetail.as_view()),
    path('users/', UserList.as_view()),
]
