# Main URL configuration for the MemorySim project
# This is the root URL configuration that routes requests to different apps

from django.contrib import admin
from django.urls import path, include

# Main URL patterns for the entire project
urlpatterns = [
    # Django admin interface
    path('admin/', admin.site.urls),
    # API endpoints - routes to api app
    path('api/', include('api.urls')),
    # Root path and other core functionality - routes to core app
    path('', include('core.urls')),
]