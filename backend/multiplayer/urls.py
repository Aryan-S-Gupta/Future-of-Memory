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
    path("votes/<str:room_code>/<str:turn_id>", views.get_voting_status_with_options),
    path("sync", views.sync_state),
    path("leave", views.leave_multiplayer_room),
    path("create_session", views.create_session),
    path('storyline/<str:session_id>/question/<str:room_code>/<str:turn_id>/<str:year>', views.display_question_and_options, name='storyline_question'),
    path('storyline/choice/<str:session_id>/<str:turn_id>/<str:year>/<str:option_id>/<str:room_code>', views.display_scenario_and_image, name='storyline_choice'),
    path("state/<str:room_code>", views.get_current_state),
    path("mini-game/submit_score", views.submit_score_single_view),
    path("mini-game/scores", views.get_scores_view),
    path("mini-game/submit_tiebreak_score", views.submit_tiebreak_score_view),

]
