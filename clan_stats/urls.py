
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ajax/search_clan/', views.search_clan_ajax, name='search_clan_ajax'),
    path('player/<str:player_tag>/', views.player_detail, name='player_detail'),
    path('clan/<str:clan_tag>/current_war/', views.current_clan_war, name='current_clan_war'),
    path('clan/<str:clan_tag>/warlog/', views.clan_war_log, name='clan_war_log'),
    path('clan/<str:clan_tag>/raids/', views.capital_raids, name='capital_raids'),
    path('rankings/', views.rankings_list, name='rankings_list'),
]