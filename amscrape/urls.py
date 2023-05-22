from django.urls import path, include, re_path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
]

"""default user views"""
urlpatterns = urlpatterns + [
    path('profile/', views.profilis, name='profile_endpoint'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name="register_endpoint"),
    path('search/', views.search, name='search_endpoint'),
    path('mysessions/<int:player_id>/new', views.PlayerSessionCreateView.as_view(), name='create_session_endpoint'),
    path('myservers/<int:player_id>/', views.GameServerListView.as_view(), name='servers_endpoint'),
    path('myservers/<int:player_id>/add', views.PlayerGameServerSelectView.as_view(), name='add_server_endpoint'),
    path('myservers/<int:player_id>/<int:gameserver_id>/', views.ServerDetailView.as_view(), name='server_endpoint'),
    path('myservers/<int:player_id>/<int:gameserver_id>/tracker/', views.PlayerTrackTargetListView.as_view(),
         name='server_trackers_endpoint'),
    path('myservers/<int:player_id>/<int:gameserver_id>/tracker/new', views.PlayerTrackTargetCreateView.as_view(),
         name='new_tracking_object_endpoint'),
]
