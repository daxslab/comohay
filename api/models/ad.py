from rest_framework import serializers, viewsets

from ads.models.ad import Ad


class AdSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedIdentityField(view_name='api:ad-detail')
    # province = serializers.HyperlinkedRelatedField(view_name='api:province-detail', read_only=True)
    # municipality = serializers.HyperlinkedRelatedField(view_name='api:municipality-detail', read_only=True)
    class Meta:
        model = Ad
        fields = '__all__'
