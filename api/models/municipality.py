from rest_framework import serializers

from ads.models.municipality import Municipality
from api.models.province import ProvinceSerializer


class MunicipalitySerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='api:municipality-detail')
    # province = serializers.StringRelatedField(read_only=True)
    # province = ProvinceSerializer(read_only=True)
    class Meta:
        model = Municipality
        fields = '__all__'

