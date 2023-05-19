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
]
