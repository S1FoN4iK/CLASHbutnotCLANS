
import os
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

# Получаем токен из переменных окружения
API_TOKEN = os.getenv('COC_API_TOKEN')
API_BASE_URL = 'https://api.clashofclans.com/v1'

class ApiError(Exception):
    """Кастомное исключение для ошибок API."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

def get_clan_data(clan_tag: str):
    """
    Получает данные клана по тегу.
    Сначала проверяет кэш, если данных нет - делает запрос к API.
    """
    # Стандартизируем тег
    if not clan_tag.startswith('#'):
        clan_tag = f'#{clan_tag}'
    
    cache_key = f'clan_data_{clan_tag}'
    cached_data = cache.get(cache_key)

    if cached_data:
        print(f"Возвращаем данные для {clan_tag} из кэша.")
        return cached_data

    print(f"Делаем запрос к API для {clan_tag}.")
    
    # Кодируем тег для URL
    clan_tag_encoded = clan_tag.replace('#', '%23')
    url = f'{API_BASE_URL}/clans/{clan_tag_encoded}'
    
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Вызовет исключение для кодов 4xx/5xx
        
        data = response.json()
        
        # Кэшируем результат на 10 минут (600 секунд)
        cache.set(cache_key, data, 600) 
        
        return data

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ApiError(f"Клан с тегом {clan_tag} не найден.", status_code=404)
        elif e.response.status_code == 403:
            raise ApiError("Доступ запрещен. Проверьте API токен и IP-адрес в настройках ключа.", status_code=403)
        else:
            raise ApiError(f"Ошибка API: {e.response.text}", status_code=e.response.status_code)
    except requests.exceptions.RequestException as e:
        raise ApiError(f"Ошибка сети: {e}")
    
def get_player_data(player_tag: str):
    """Получает детальную информацию по игроку."""
    if not player_tag.startswith('#'):
        player_tag = f'#{player_tag}'
    
    cache_key = f'player_data_{player_tag}'
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"Возвращаем данные игрока {player_tag} из кэша.")
        return cached_data

    print(f"Делаем запрос к API для игрока {player_tag}.")
    player_tag_encoded = player_tag.replace('#', '%23')
    url = f'{API_BASE_URL}/players/{player_tag_encoded}'
    
    headers = {'Authorization': f'Bearer {API_TOKEN}'}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        cache.set(cache_key, data, 600) # Кэшируем на 10 минут
        return data
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise ApiError(f"Игрок с тегом {player_tag} не найден.", 404)
        raise ApiError(f"Ошибка API: {e.response.text}", e.response.status_code)
    except requests.exceptions.RequestException as e:
        raise ApiError(f"Ошибка сети: {e}")