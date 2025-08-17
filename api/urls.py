from django.urls import path
from . import views

urlpatterns = [
    path('static-question', views.get_static_question),
    path('static-story', views.get_static_story),
]