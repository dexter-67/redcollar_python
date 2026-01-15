from django.urls import path
from .views import PointViewSet, MessageViewSet


points_search_view = PointViewSet.as_view({'get': 'search'})
messages_search_view = MessageViewSet.as_view({'get': 'search'})

urlpatterns = [
    path('points/', PointViewSet.as_view({
        'post': 'create',
        'get': 'list'
    }), name='point-list-create'),
    path('points/messages/', MessageViewSet.as_view({
        'post': 'create'
    }), name='message-create'),
    path('points/search/', points_search_view, name='points-search'),
    path('messages/search/', messages_search_view, name='messages-search'),
    path('points/<int:pk>/', PointViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='point-detail'),

    path('messages/<int:pk>/', MessageViewSet.as_view({
        'get': 'retrieve',
        'delete': 'destroy'
    }), name='message-detail'),
]
