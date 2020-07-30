from rest_framework import serializers

from ads.models.ad import Ad
from api.models.municipality import MunicipalitySerializer
from api.models.province import ProvinceSerializer


class AdSerializer(serializers.ModelSerializer):
    province = ProvinceSerializer()
    municipality = MunicipalitySerializer()
    class Meta:
        model = Ad
        fields = '__all__'
