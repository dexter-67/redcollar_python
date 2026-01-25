from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import Message, Point


@admin.register(Point)
class PointAdmin(GISModelAdmin):
    gis_widget_kwargs = {
        'attrs': {
            'default_lon': 37.6178,
            'default_lat': 55.7558,
            'default_zoom': 10,
        },
    }

    list_display = ('id', 'name',
                    'created_by',
                    'get_latitude',
                    'get_longitude',
                    'created_at')
    list_filter = ('created_by', 'created_at')
    search_fields = ('name', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')

    def get_latitude(self, obj):
        return round(obj.location.y, 6) if obj.location else None
    get_latitude.short_description = 'Широта'
    get_latitude.admin_order_field = 'location'

    def get_longitude(self, obj):
        return round(obj.location.x, 6) if obj.location else None
    get_longitude.short_description = 'Долгота'
    get_longitude.admin_order_field = 'location'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'text_preview', 'point_link', 'created_by', 'created_at')
    list_filter = ('created_by', 'created_at', 'point')
    search_fields = ('text', 'created_by__username', 'point__name')
    readonly_fields = ('created_at', 'updated_at')

    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Текст (превью)'

    def point_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:core_point_change', args=[obj.point.id])
        point_name = obj.point.name or f"Точка #{obj.point.id}"
        return format_html('<a href="{}">{}</a>', url, point_name)
    point_link.short_description = 'Точка'
    point_link.admin_order_field = 'point'
