import django_filters

from .models import Restaurant


class RestaurantFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    city = django_filters.CharFilter(field_name='restaurantaddress__address__city', lookup_expr='iexact')

    class Meta:
        model = Restaurant
        fields = ['name', 'city']