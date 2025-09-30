"""
URL configuration for the API endpoints related to the storyline feature.
Maps URL paths to their corresponding view functions.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('create_session', views.create_session, name='create_session'),
    path('start_prerender', views.start_prerendering, name='start_prerendering'),
    path('storyline/<int:session_id>/question', views.display_question_and_options, name='display_question_and_options'),
    path('storyline/start/<int:session_id>/<int:turn_id>/<int:year>/<int:option_id>',
         views.display_scenario_and_image, name='storyline_scenario'),
    path('storyline/choice', views.get_story_result_by_choice, name='storyline_choice'),
    path('storyline/result', views.get_story_result, name='storyline_result'),
    path('rag/retrieve', views.rag_retrieve, name='rag_retrieve'),
    path('storyline/result', views.get_story_result, name='storyline_result'),
    path('rag/fun_facts', views.retrieve_fun_facts_api, name='fun_facts'),
]