import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point as GeoPoint
from core.models import Point, Message


@pytest.fixture(autouse=True)
def clear_db():
    Point.objects.all().delete()
    Message.objects.all().delete()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='test123')


@pytest.fixture
def another_user(db):
    return User.objects.create_user(username='another', password='test123')


@pytest.fixture
def auth_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def unauth_client():
    return APIClient()


@pytest.fixture
def point_amsterdam(user):
    return Point.objects.create(
        created_by=user,
        name="Amsterdam Centraal",
        location=GeoPoint(4.900225, 52.379189, srid=4326)
    )


@pytest.fixture
def another_point(another_user):
    return Point.objects.create(
        created_by=another_user,
        name="Чужая точка",
        location=GeoPoint(4.895, 52.370, srid=4326)
    )


@pytest.fixture
def points(user):
    coords = [
        ("Центр", 4.895168, 52.370216),
        ("Аэропорт", 4.763889, 52.308056),
        ("Берлин", 13.4050, 52.5200),
    ]

    points_list = []
    for name, lon, lat in coords:
        point = Point.objects.create(
            created_by=user,
            name=name,
            location=GeoPoint(lon, lat, srid=4326)
        )
        points_list.append(point)

    return points_list


@pytest.mark.django_db
class TestPointAPI:

    def test_create_point_success(self, auth_client):
        data = {
            "name": "Эйфелева башня",
            "latitude": 48.8584,
            "longitude": 2.2945
        }
        resp = auth_client.post('/api/points/', data, format='json')
        assert resp.status_code == 201
        assert resp.data['name'] == "Эйфелева башня"
        assert 'latitude' in resp.data
        assert 'longitude' in resp.data
        assert Point.objects.filter(name="Эйфелева башня").exists()

    def test_create_point_minimal_data(self, auth_client):
        data = {
            "latitude": 55.7558,
            "longitude": 37.6173
        }
        resp = auth_client.post('/api/points/', data, format='json')
        assert resp.status_code == 201
        assert resp.data['latitude'] == 55.7558
        assert resp.data['longitude'] == 37.6173

    def test_create_point_invalid_coords(self, auth_client):
        data = {
            "name": "Ошибка",
            "latitude": 91,
            "longitude": 2.2945
        }
        resp = auth_client.post('/api/points/', data, format='json')
        assert resp.status_code == 400
        assert 'latitude' in resp.data

    def test_create_point_missing_coords(self, auth_client):
        data = {"name": "Без координат"}
        resp = auth_client.post('/api/points/', data, format='json')
        assert resp.status_code == 400

    def test_create_point_unauth(self, unauth_client):
        data = {"name": "Тест", "latitude": 52.37, "longitude": 4.89}
        resp = unauth_client.post('/api/points/', data, format='json')
        assert resp.status_code == 401

    def test_search_radius_10km(self, auth_client, points):
        resp = auth_client.get('/api/points/search/', {
            'latitude': 52.37,
            'longitude': 4.89,
            'radius': 20
        })
        assert resp.status_code == 200
        items = resp.data.get('results', resp.data)
        assert len(items) >= 2
        assert all('distance_km' in item for item in items)

    def test_search_radius_1km(self, auth_client, points):
        resp = auth_client.get('/api/points/search/', {
            'latitude': 52.37,
            'longitude': 4.89,
            'radius': 1
        })
        assert resp.status_code == 200
        items = resp.data.get('results', resp.data)
        assert len(items) == 1
        assert items[0]['name'] == "Центр"

    def test_search_invalid_radius(self, auth_client):
        resp = auth_client.get('/api/points/search/', {
            'latitude': 52.37,
            'longitude': 4.89,
            'radius': -5
        })
        assert resp.status_code == 400

    def test_search_missing_params(self, auth_client):
        resp = auth_client.get('/api/points/search/', {'latitude': 52.37})
        assert resp.status_code == 400

    def test_search_unauth(self, unauth_client):
        resp = unauth_client.get('/api/points/search/', {
            'latitude': 52.37,
            'longitude': 4.89,
            'radius': 10
        })
        assert resp.status_code == 401

    def test_update_point_name_only(self, auth_client, point_amsterdam):
        data = {"name": "Новое название"}
        resp = auth_client.patch(f'/api/points/{point_amsterdam.id}/', data, format='json')
        assert resp.status_code == 200
        assert resp.data['name'] == "Новое название"
        assert resp.data['latitude'] == 52.379189
        assert resp.data['longitude'] == 4.900225


@pytest.mark.django_db
class TestMessageAPI:

    def test_message_create_success(self, auth_client, point_amsterdam):
        data = {
            "point_id": point_amsterdam.id,
            "text": "Классное место!"
        }
        resp = auth_client.post('/api/points/messages/', data, format='json')
        assert resp.status_code == 201
        assert resp.data['text'] == "Классное место!"
        assert resp.data['point']['id'] == point_amsterdam.id
        assert Message.objects.filter(text="Классное место!").exists()

    def test_message_create_to_foreign_point(self, auth_client, another_point):
        data = {
            "point_id": another_point.id,
            "text": "Классное место у другого пользователя!"
        }
        resp = auth_client.post('/api/points/messages/', data, format='json')
        assert resp.status_code == 201
        assert Message.objects.count() == 1

    def test_message_create_nonexistent_point(self, auth_client):
        data = {
            "point_id": 99999,
            "text": "Сообщение"
        }
        resp = auth_client.post('/api/points/messages/', data, format='json')
        assert resp.status_code == 400

    def test_message_create_empty_text(self, auth_client, point_amsterdam):
        data = {
            "point_id": point_amsterdam.id,
            "text": ""
        }
        resp = auth_client.post('/api/points/messages/', data, format='json')
        assert resp.status_code == 400

    def test_message_create_unauth(self, unauth_client, point_amsterdam):
        data = {"point_id": point_amsterdam.id, "text": "Без авторизации"}
        resp = unauth_client.post('/api/points/messages/', data, format='json')
        assert resp.status_code == 401

    def test_message_search_own_messages(self, auth_client, user, point_amsterdam):
        Message.objects.create(
            point=point_amsterdam,
            created_by=user,
            text="Тестовое сообщение"
        )
        resp = auth_client.get('/api/messages/search/', {
            'latitude': 52.37,
            'longitude': 4.89,
            'radius': 5
        })
        assert resp.status_code == 200
        if 'results' in resp.data:
            items = resp.data['results']
        else:
            items = resp.data
        assert len(items) == 1
        assert 'point_distance_km' in items[0]
        assert items[0]['point_distance_km'] is not None

    def test_message_search_all_users_messages(self, auth_client, another_user, another_point):
        Message.objects.create(
            point=another_point,
            created_by=another_user,
            text="Сообщение от другого пользователя"
        )
        resp = auth_client.get('/api/messages/search/', {
            'latitude': 52.37,
            'longitude': 4.89,
            'radius': 10
        })
        assert resp.status_code == 200
        if 'results' in resp.data:
            items = resp.data['results']
        else:
            items = resp.data
        assert len(items) == 1
        assert items[0]['text'] == "Сообщение от другого пользователя"

    def test_message_search_with_distance(self, auth_client, user, point_amsterdam):
        point_amsterdam.location = GeoPoint(4.900225, 52.379189 + 0.009, srid=4326)
        point_amsterdam.save()
        Message.objects.create(
            point=point_amsterdam,
            created_by=user,
            text="Сообщение"
        )
        resp = auth_client.get('/api/messages/search/', {
            'latitude': 52.379189,
            'longitude': 4.900225,
            'radius': 2
        })
        assert resp.status_code == 200
        if 'results' in resp.data:
            items = resp.data['results']
        else:
            items = resp.data
        assert len(items) == 1
        distance = items[0]['point_distance_km']
        assert distance is not None
        assert 0.9 < distance < 1.1

    def test_message_search_invalid_params(self, auth_client):
        resp = auth_client.get('/api/messages/search/', {
            'latitude': 91,
            'longitude': 4.89,
            'radius': 10
        })
        assert resp.status_code == 400

    def test_message_search_unauth(self, unauth_client):
        resp = unauth_client.get('/api/messages/search/', {
            'latitude': 52.37,
            'longitude': 4.89,
            'radius': 10
        })
        assert resp.status_code == 401
