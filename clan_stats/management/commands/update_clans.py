
from django.core.management.base import BaseCommand
from clan_stats import api_client
from clan_stats.models import Clan, Player
from django.utils import timezone
import time

# Список кланов, которые мы хотим отслеживать
TRACKED_CLAN_TAGS = [
    '#2PPQYC2Q',  
]

class Command(BaseCommand):
    help = 'Обновляет информацию по отслеживаемым кланам из Supercell API'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начало обновления кланов...'))

        for tag in TRACKED_CLAN_TAGS:
            self.stdout.write(f'Обновляем клан {tag}...')
            try:
                # Используем тот же код, что и в AJAX view
                clan_data = api_client.get_clan_data(tag)
                
                clan_instance, created = Clan.objects.update_or_create(
                    tag=clan_data['tag'],
                    defaults={
                        'name': clan_data['name'],
                        'clan_level': clan_data['clanLevel'],
                        'clan_points': clan_data['clanPoints'],
                        'members_count': clan_data['members']
                    }
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Клан {clan_data["name"]} добавлен в базу.'))
                else:
                    self.stdout.write(f'Клан {clan_data["name"]} обновлен.')

                # Обновляем игроков
                for member_data in clan_data['memberList']:
                    Player.objects.update_or_create(
                        tag=member_data['tag'],
                        defaults={ 'name': member_data['name'], 'clan': clan_instance, 'role': member_data['role'], 'exp_level': member_data['expLevel'], 'trophies': member_data['trophies'], 'donations': member_data['donations'], 'donations_received': member_data['donationsReceived']}
                    )
                
                # Задержка, чтобы не превысить лимиты API
                time.sleep(1) 

            except api_client.ApiError as e:
                self.stderr.write(self.style.ERROR(f'Ошибка при обновлении клана {tag}: {e}'))
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Непредвиденная ошибка для клана {tag}: {e}'))

        self.stdout.write(self.style.SUCCESS('Обновление завершено!'))