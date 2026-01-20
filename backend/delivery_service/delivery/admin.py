from django.contrib import admin
from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_id',
        'status',
        'distance_km',
        'estimated_time',
        'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'start_location', 'end_location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'status')
        }),
        ('Route Details', {
            'fields': ('start_location', 'end_location', 'distance_km', 'estimated_time')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

