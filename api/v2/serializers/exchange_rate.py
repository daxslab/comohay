from rest_framework import serializers

from currencies.models.exchange_rate import ExchangeRate
from api.v1.serializers.exchange_rate import ExchangeRateSerializer as ExchangeRateSerializerV1
from api.v1.serializers.exchange_rate import ActiveExchangeRateSerializer as ActiveExchangeRateSerializerV1


class ExchangeRateSerializerV2(ExchangeRateSerializerV1):
    class Meta:
        model = ExchangeRate
        fields = '__all__'


class ActiveExchangeRateSerializerV2(ActiveExchangeRateSerializerV1):
    buy_exchange_rate = ExchangeRateSerializerV2()
    sell_exchange_rate = ExchangeRateSerializerV2()
    mid_exchange_rate = ExchangeRateSerializerV2()
