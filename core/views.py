from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from django.contrib.gis.geos import Point as GeoPoint
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from .models import Point, Message
from .serializers import PointSerializer, MessageSerializer


class PointViewSet(viewsets.ModelViewSet):
    queryset = Point.objects.all()
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action not in ['search']:
            return self.queryset.filter(created_by=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['GET'], url_path='search')
    def search(self, request):
        try:
            lat = float(request.query_params['latitude'])
            lon = float(request.query_params['longitude'])
            radius = float(request.query_params.get('radius', 10))
        except (KeyError, ValueError, TypeError):
            return Response(
                {"detail": "Обязательные параметры: latitude, longitude, radius (числа)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return Response(
                {"detail": "Недопустимые значения широты или долготы"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if radius <= 0:
            return Response(
                {"detail": "Радиус должен быть больше 0 км"},
                status=status.HTTP_400_BAD_REQUEST
            )

        radius = min(radius, 1000)
        center = GeoPoint(lon, lat, srid=4326)

        queryset = (
            self.get_queryset()
            .filter(location__distance_lte=(center, D(km=radius)))
            .annotate(distance=Distance('location', center))
            .order_by('distance')
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MessageViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action not in ['search']:
            return self.queryset.filter(created_by=self.request.user).select_related('point', 'created_by')
        return self.queryset.select_related('point', 'created_by')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['GET'], url_path='search')
    def search(self, request):
        try:
            lat = float(request.query_params['latitude'])
            lon = float(request.query_params['longitude'])
            radius = float(request.query_params.get('radius', 10))
        except (KeyError, ValueError, TypeError):
            return Response(
                {"detail": "Обязательные параметры: latitude, longitude, radius (числа)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return Response(
                {"detail": "Недопустимые значения широты или долготы"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if radius <= 0:
            return Response(
                {"detail": "Радиус должен быть больше 0 км"},
                status=status.HTTP_400_BAD_REQUEST
            )

        radius = min(radius, 1000)
        center = GeoPoint(lon, lat, srid=4326)

        queryset = (
            self.get_queryset()
            .filter(point__location__distance_lte=(center, D(km=radius)))
            .annotate(distance=Distance('point__location', center))
            .order_by('distance')
        )

        for msg in queryset:
            msg.distance = getattr(msg, 'distance', None)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
