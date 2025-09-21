"""
URL configuration for the API endpoints related to the storyline feature.
Maps URL paths to their corresponding view functions.
"""
from django.urls import path
from . import views

urlpatterns = [
    path("multiplayer/create", views.create_multiplayer_room),
    path("multiplayer/join", views.join_multiplayer_room),
    path("multiplayer/sync", views.sync_state),
    path("multiplayer/state/<str:room_code>", views.get_current_state),
]
