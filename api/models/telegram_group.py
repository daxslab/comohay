from rest_framework import serializers
from ads.models import TelegramGroup
from api.models.municipality import MunicipalitySerializer
from api.models.province import ProvinceSerializer


class TelegramGroupSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer()
    municipality = MunicipalitySerializer()

    class Meta:
        model = TelegramGroup
        fields = '__all__'
