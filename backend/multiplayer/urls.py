"""
URL configuration for the API endpoints related to the storyline feature.
Maps URL paths to their corresponding view functions.
"""
from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create_multiplayer_room),
    path("join", views.join_multiplayer_room),
    path("rooms", views.list_room_codes),
    path("sync", views.sync_state),
    path("state/<str:room_code>", views.get_current_state),
]
