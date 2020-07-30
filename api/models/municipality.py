from rest_framework import serializers

from ads.models.municipality import Municipality


class MunicipalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipality
        fields = '__all__'
