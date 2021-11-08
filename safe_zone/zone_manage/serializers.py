from rest_framework import serializers
from .models import InitSafeZone


class InitSafeZoneSer(serializers.ModelSerializer):
    class Meta:
        model = InitSafeZone
        fields = ['latitude', 'longitude', 'user']