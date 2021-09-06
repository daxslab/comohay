from rest_framework import serializers
from currencies.models.currencyad import CurrencyAd


class CurrencyAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyAd
        exclude = ['id']