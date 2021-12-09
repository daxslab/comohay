from rest_framework import serializers
from ads.models import TelegramGroup
from api.v1.serializers.municipality import MunicipalitySerializer
from api.v1.serializers.province import ProvinceSerializer


class TelegramGroupSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer()
    municipality = MunicipalitySerializer()

    class Meta:
        model = TelegramGroup
        fields = '__all__'
