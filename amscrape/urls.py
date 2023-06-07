from django.urls import path, include, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
]

"""admin views"""

"""user views"""
urlpatterns = urlpatterns + [
    path('profile/', views.profilis, name='profile_endpoint'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name="register_endpoint"),
    path('search/', views.search, name='search_endpoint'),
    path('mysessions/<int:player_id>/new', views.PlayerSessionCreateView.as_view(), name='create_session_endpoint'),
    path('myservers/<int:player_id>/', views.GameServerListView.as_view(), name='servers_endpoint'),
    path('myservers/<int:player_id>/add', views.PlayerGameServerSelectView.as_view(), name='add_server_endpoint'),
    path('myserver/<int:pk>/', views.ServerDetailView.as_view(), name='server_endpoint'),
    path('myserver/<int:player_game_server_id>/trackers/', views.PlayerTrackTargetListView.as_view(),
         name='server_trackers_endpoint'),
    path('myserver/<int:player_game_server_id>/tracker/new', views.PlayerTrackTargetCreateView.as_view(),
         name='new_tracking_object_endpoint'),
    path('myserver/parameters/<int:pk>/', views.PlayerGameServerUpdateView.as_view(),
         name='update_server_parameters_endpoint'),
    path('myserver/<int:player_game_server_id>/statistics/', views.KingdomStatListView.as_view(),
         name='kingdom_statistics_endpoint'),
    path('myserver/<int:player_game_server_id>/deletestatistics/', views.KingdomStatDeleteView.as_view(),
         name='kingdomstat_delete_endpoint'),
    path('myserver/<int:player_game_server_id>/statistics/<str:selected_key>/',
         views.KingdomStatFilteredListView.as_view(), name='kingdom_stats_filtered_endpoint'),
    path('myserver/<int:player_game_server_id>/starttracking/', views.PeriodicTaskCreateView.as_view(),
         name='start_tracking_endpoint'),
    path('myserver/<int:player_game_server_id>/stoptracking/', views.PeriodicTaskPauseView.as_view(),
         name='stop_tracking_endpoint'),
    path('myserver/<int:player_game_server_id>/<int:track_target_id>/newcondition',
         views.TrackTargetConditionCreateView.as_view(), name='add_condition_endpoint'),
    path('myserver/<int:player_game_server_id>/<int:track_target_id>/conditions',
         views.ConditionListView.as_view(), name='condition_list_endpoint'),
    path('myserver/<int:player_game_server_id>/<int:track_target_id>/condition/<int:pk>',
         views.ConditionDeleteView.as_view(), name='condition_delete_endpoint'),
]
