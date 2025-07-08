
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/search_clan/', views.search_clan_ajax, name='search_clan_ajax'),
    path('player/<str:player_tag>/', views.player_detail, name='player_detail'),
]