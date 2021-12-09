from rest_framework import serializers

from ads.models.ad import Ad
from api.v1.serializers.municipality import MunicipalitySerializer
from api.v1.serializers.province import ProvinceSerializer


class AdSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer()
    municipality = MunicipalitySerializer()
    class Meta:
        model = Ad
        fields = '__all__'
