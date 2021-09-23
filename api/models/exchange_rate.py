from rest_framework import serializers
from currencies.models.exchange_rate import ExchangeRate, ActiveExchangeRate


class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        exclude = ['id']


class ActiveExchangeRateSerializer(serializers.Serializer):

    source_currency_iso = serializers.CharField(max_length=3)
    target_currency_iso = serializers.CharField(max_length=3)
    buy_exchange_rate = ExchangeRateSerializer()
    sell_exchange_rate = ExchangeRateSerializer()
    mid_exchange_rate = ExchangeRateSerializer()
    target_datetime = serializers.DateTimeField()

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
