from rest_framework import serializers
from api.models.ad import AdSerializer
from currencies.models.currencyad import CurrencyAd


class CurrencyAdSerializer(serializers.ModelSerializer):
    ad = AdSerializer()

    class Meta:
        model = CurrencyAd
        fields = '__all__'
