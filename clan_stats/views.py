
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from . import api_client
from .models import Clan, Player
from django.shortcuts import get_object_or_404
from django.utils import timezone

def index(request):
    """Отображает главную страницу с формой поиска."""
    return render(request, 'clan_stats/index.html')

def search_clan_ajax(request):
    """
    Обрабатывает AJAX-запрос, ищет клан, обновляет БД
    и возвращает HTML-фрагмент с результатами.
    """
    clan_tag = request.POST.get('clan_tag')
    if not clan_tag:
        return HttpResponseBadRequest("Тег клана не может быть пустым.")

    try:
        # 1. Получаем данные из API (или кэша)
        clan_data = api_client.get_clan_data(clan_tag)
        
        # 2. Сохраняем/обновляем данные в БД
        clan_instance, _ = Clan.objects.update_or_create(
            tag=clan_data['tag'],
            defaults={
                'name': clan_data['name'],
                'clan_level': clan_data['clanLevel'],
                'clan_points': clan_data['clanPoints'],
                'members_count': clan_data['members']
            }
        )
        
        # Сохраняем/обновляем игроков
        for member_data in clan_data['memberList']:
            Player.objects.update_or_create(
                tag=member_data['tag'],
                defaults={
                    'name': member_data['name'],
                    'clan': clan_instance,
                    'role': member_data['role'],
                    'exp_level': member_data['expLevel'],
                    'trophies': member_data['trophies'],
                    'donations': member_data['donations'],
                    'donations_received': member_data['donationsReceived']
                }
            )

        # 3. Отдаем отрендеренный HTML-фрагмент
        return render(request, 'clan_stats/_clan_results_partial.html', {'clan_data': clan_data})
        
    except api_client.ApiError as e:
        # Возвращаем HTML с ошибкой
        return HttpResponse(f'<div class="alert alert-danger mt-3">{e}</div>', status=e.status_code or 400)
    
def player_detail(request, player_tag):
    # Добавляем # обратно к тегу для API
    full_tag = f"#{player_tag}"
    
    try:
        player_data = api_client.get_player_data(full_tag)

        # Обновляем нашего игрока в БД
        # Используем get_object_or_404, чтобы убедиться, что игрок уже есть в БД
        player_instance = get_object_or_404(Player, tag=full_tag)
        
        # Извлекаем уровни героев (с проверкой на их наличие)
        def get_hero_level(hero_name):
            return next((h['level'] for h in player_data.get('heroes', []) if h['name'] == hero_name), None)

        player_instance.town_hall_level = player_data.get('townHallLevel')
        player_instance.barbarian_king_level = get_hero_level('Barbarian King')
        player_instance.archer_queen_level = get_hero_level('Archer Queen')
        player_instance.grand_warden_level = get_hero_level('Grand Warden')
        player_instance.royal_champion_level = get_hero_level('Royal Champion')
        player_instance.details_last_updated = timezone.now()
        player_instance.save()
        
        context = {
            'player': player_instance,
            'api_data': player_data # передаем все данные из API для отображения
        }
        return render(request, 'clan_stats/player_detail.html', context)
        
    except api_client.ApiError as e:
        return render(request, 'clan_stats/error_page.html', {'error': e})

def current_clan_war(request, clan_tag):
    full_tag = f"#{clan_tag}"
    try:
        war_data = api_client.get_current_war(full_tag)
        context = {'war_data': war_data}
        return render(request, 'clan_stats/current_war.html', context)
    except api_client.ApiError as e:
        return render(request, 'clan_stats/error_page.html', {'error': e})

def clan_war_log(request, clan_tag):
    full_tag = f"#{clan_tag}"
    try:
        war_log_data = api_client.get_war_log(full_tag)
        context = {'war_log_data': war_log_data}
        return render(request, 'clan_stats/war_log.html', context)
    except api_client.ApiError as e:
        return render(request, 'clan_stats/error_page.html', {'error': e})

def capital_raids(request, clan_tag):
    full_tag = f"#{clan_tag}"
    try:
        raids_data = api_client.get_capital_raids(full_tag)
        context = {
            'raids_data': raids_data,
            'clan_tag': clan_tag # Передаем тег для кнопки "назад"
        }
        return render(request, 'clan_stats/capital_raids.html', context)
    except api_client.ApiError as e:
        return render(request, 'clan_stats/error_page.html', {'error': e})

def rankings_list(request):
    context = {}
    try:
        locations_data = api_client.get_locations()
        # Оставляем только страны, убираем континенты
        countries = [loc for loc in locations_data.get('items', []) if loc.get('isCountry')]
        context['locations'] = countries
        
        location_id = request.GET.get('location_id')
        if location_id:
            rankings_data = api_client.get_clan_rankings(location_id)
            context['rankings'] = rankings_data.get('items', [])
            context['selected_location_id'] = int(location_id)

    except api_client.ApiError as e:
        context['error'] = e

    return render(request, 'clan_stats/rankings.html', context)        