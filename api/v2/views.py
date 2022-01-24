import datetime

from rest_framework.generics import get_object_or_404
from rest_framework.status import HTTP_404_NOT_FOUND

import currencies.services.exchange_rate_service

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from api.v2.serializers.exchange_rate import ActiveExchangeRateSerializerV2, ExchangeRateSerializerV2
from currencies.models import ExchangeRate


class ActiveExchangeRatesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        target_datetime_str = self.request.query_params.get('target_datetime', default=None)
        limit_datetime_str = self.request.query_params.get('limit_datetime', default=None)

        if target_datetime_str is None:
            target_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        else:
            target_datetime = datetime.datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=datetime.timezone.utc
            )

        if limit_datetime_str is None:
            limit_datetime = target_datetime - datetime.timedelta(days=15)
        else:
            limit_datetime = datetime.datetime.strptime(limit_datetime_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=datetime.timezone.utc
            )

        active_exchange_rates = currencies.services.exchange_rate_service.get_active_exchange_rate_list(
            ref_type=ExchangeRate.TYPE_MID,
            target_datetime=target_datetime,
            limit_datetime=limit_datetime
        )

        serializer = ActiveExchangeRateSerializerV2(active_exchange_rates, many=True)

        return Response(serializer.data)


class ActiveExchangeRateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, source_currency_iso, target_currency_iso):

        target_datetime_str = self.request.query_params.get('target_datetime', default=None)
        limit_datetime_str = self.request.query_params.get('limit_datetime', default=None)

        if target_datetime_str is None:
            target_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        else:
            target_datetime = datetime.datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=datetime.timezone.utc
            )

        if limit_datetime_str is None:
            limit_datetime = target_datetime - datetime.timedelta(days=30)
        else:
            limit_datetime = datetime.datetime.strptime(limit_datetime_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=datetime.timezone.utc
            )

        active_exchange_rate = currencies.services.exchange_rate_service.get_active_exchange_rate(
            source_currency_iso=source_currency_iso,
            target_currency_iso=target_currency_iso,
            ref_type=ExchangeRate.TYPE_MID,
            target_datetime=target_datetime,
            limit_datetime=limit_datetime
        )

        if not active_exchange_rate:
            return Response(HTTP_404_NOT_FOUND)

        serializer = ActiveExchangeRateSerializerV2(active_exchange_rate)

        return Response(serializer.data)


class OpenExchangeRateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        exchange_rate = get_object_or_404(ExchangeRate, id=id)
        open_exchange_rate = currencies.services.exchange_rate_service.get_open_exchange_rate_of(exchange_rate)
        serializer = ExchangeRateSerializerV2(open_exchange_rate)
        return Response(serializer.data)


class FiftyTwoWeekHighExchangeRateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        exchange_rate = get_object_or_404(ExchangeRate, id=id)
        high_exchange_rate = currencies.services.exchange_rate_service.get_52_week_high_exchange_rate_of(exchange_rate)
        serializer = ExchangeRateSerializerV2(high_exchange_rate)
        return Response(serializer.data)


class FiftyTwoWeekLowExchangeRateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        exchange_rate = get_object_or_404(ExchangeRate, id=id)
        low_exchange_rate = currencies.services.exchange_rate_service.get_52_week_low_exchange_rate_of(exchange_rate)
        serializer = ExchangeRateSerializerV2(low_exchange_rate)
        return Response(serializer.data)
