"""
URL configuration for the API endpoints related to the storyline feature.
Maps URL paths to their corresponding view functions.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('storyline/start', views.get_story_scenario, name='storyline_background'),
    path('storyline/question', views.get_story_question, name='storyline_question'),
    path('storyline/choice', views.get_story_result_by_choice, name='storyline_choice'),
    path('storyline/result', views.get_story_result, name='storyline_result'),
    # frontend continuously check status
    path('render/status/<str:world_id>', views.render_status, name='image_status'),
    # image once ready, serve from this url
    path('render/<str:world_id>', views.render_image, name='render_image'), 
]