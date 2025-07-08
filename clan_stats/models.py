
from django.db import models

class Clan(models.Model):
    tag = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    clan_level = models.IntegerField()
    clan_points = models.IntegerField()
    members_count = models.IntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.tag})"

class Player(models.Model):
    tag = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    clan = models.ForeignKey(Clan, on_delete=models.SET_NULL, null=True, related_name='members')
    role = models.CharField(max_length=50)
    exp_level = models.IntegerField()
    trophies = models.IntegerField()
    donations = models.IntegerField()
    donations_received = models.IntegerField()
    
    town_hall_level = models.IntegerField(null=True, blank=True)
    barbarian_king_level = models.IntegerField(null=True, blank=True)
    archer_queen_level = models.IntegerField(null=True, blank=True)
    grand_warden_level = models.IntegerField(null=True, blank=True)
    royal_champion_level = models.IntegerField(null=True, blank=True)

    last_updated = models.DateTimeField(auto_now=True)
    details_last_updated = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.tag})"