from rest_framework import serializers
from stats.models.exchange_rate import ExchangeRate


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        exclude = ['id']
