# URL configuration for the core app
# This module defines the URL patterns for the core application

from django.urls import path
from . import views

# URL patterns for core app routes
urlpatterns = [
    # Root path - displays basic backend status message
    path('', views.index),
]