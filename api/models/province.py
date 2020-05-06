from rest_framework import serializers, viewsets

from ads.models.province import Province


class ProvinceSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='api:province-detail')
    class Meta:
        model = Province
        fields = '__all__'
