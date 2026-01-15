from rest_framework import serializers
from django.contrib.gis.geos import Point as GeoPoint
from .models import Point as PointModel, Message


class PointSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(
        write_only=True,
        required=False,
        min_value=-90,
        max_value=90,
        error_messages={
            'min_value': 'Широта должна быть ≥ -90°',
            'max_value': 'Широта должна быть ≤ 90°',
        }
    )
    longitude = serializers.FloatField(
        write_only=True,
        required=False,
        min_value=-180,
        max_value=180,
        error_messages={
            'min_value': 'Долгота должна быть ≥ -180°',
            'max_value': 'Долгота должна быть ≤ 180°',
        }
    )
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    distance_km = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PointModel
        fields = [
            'id', 'name', 'latitude', 'longitude', 'created_by',
            'created_at', 'updated_at', 'distance_km'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'distance_km']
        extra_kwargs = {
            'name': {
                'max_length': 255,
                'allow_blank': True,
                'required': False,
                'error_messages': {
                    'max_length': 'Название точки не должно превышать 255 символов'
                }
            }
        }

    def validate(self, attrs):
        lat = attrs.pop('latitude', None)
        lon = attrs.pop('longitude', None)
        location = attrs.get('location')

        if self.context['request'].method == 'POST':
            if lat is None or lon is None:
                raise serializers.ValidationError({
                    'detail': 'При создании точки необходимо указать latitude и longitude'
                })
        if (lat is not None or lon is not None) and location is not None:
            raise serializers.ValidationError({
                'detail': 'Укажите либо latitude+longitude, либо location, но не оба варианта'
            })
        if lat is not None and lon is not None:
            location = GeoPoint(lon, lat, srid=4326)
            attrs['location'] = location
        elif lat is not None or lon is not None:
            raise serializers.ValidationError({
                'detail': 'Необходимо указать обе координаты: latitude и longitude'
            })
        elif location is not None:
            if not isinstance(location, GeoPoint):
                raise serializers.ValidationError({
                    'location': 'Поле location должно быть объектом GeoPoint'
                })
            if location.srid != 4326:
                location.transform(4326)
        elif self.context['request'].method == 'POST':
            pass

        return attrs

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.location:
            ret['latitude'] = round(instance.location.y, 6)
            ret['longitude'] = round(instance.location.x, 6)
        ret.pop('created_by', None)
        return ret

    def get_distance_km(self, obj):
        if hasattr(obj, 'distance') and obj.distance is not None:
            return round(obj.distance.km, 2)
        return None


class MessageSerializer(serializers.ModelSerializer):
    point_id = serializers.PrimaryKeyRelatedField(
        queryset=PointModel.objects.all(),
        source='point',
        write_only=True,
        error_messages={
            'does_not_exist': 'Указанной точки не существует',
            'incorrect_type': 'point_id должен быть целым числом (ID)',
        }
    )
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    point = serializers.SerializerMethodField(read_only=True)
    point_distance_km = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'point_id',
            'point',
            'text',
            'created_by',
            'created_at',
            'updated_at',
            'point_distance_km',
        ]
        read_only_fields = [
            'id',
            'point',
            'created_by',
            'created_at',
            'updated_at',
            'point_distance_km',
        ]
        extra_kwargs = {
            'text': {
                'min_length': 1,
                'max_length': 2000,
                'error_messages': {
                    'blank': 'Текст сообщения не может быть пустым',
                    'min_length': 'Текст сообщения должен содержать хотя бы 1 символ',
                    'max_length': 'Текст сообщения не должен превышать 2000 символов'
                }
            }
        }

    def validate(self, attrs):
        text = attrs.get('text', '').strip()
        if not text:
            raise serializers.ValidationError({
                'text': 'Текст сообщения не может быть пустым или состоять только из пробелов'
            })
        attrs['text'] = text
        return attrs

    def get_point(self, obj):
        if obj.point:
            return {
                'id': obj.point.id,
                'name': obj.point.name or f"Точка #{obj.point.id}",
                'latitude': round(obj.point.location.y, 6) if obj.point.location else None,
                'longitude': round(obj.point.location.x, 6) if obj.point.location else None,
            }
        return None

    def get_point_distance_km(self, obj):
        if hasattr(obj, 'distance') and obj.distance is not None:
            return round(obj.distance.km, 2)
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret.pop('created_by', None)
        return ret
