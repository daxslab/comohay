import datetime
import currencies.services.exchange_rate_service

from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from haystack.query import EmptySearchQuerySet, SearchQuerySet
from rest_auth.app_settings import create_token
from rest_auth.utils import jwt_encode
from rest_auth.views import LoginView
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from rest_framework.views import APIView
from rest_framework import generics
from ads.models import TelegramGroup
from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province
from api.v1.serializers.ad import AdSerializer
from api.v1.serializers.adsearch import AdSearchSerializer
from api.v1.serializers.classifieds_platform import ClassifiedsPlatformSerializer
from api.v1.serializers.currencyad import CurrencyAdSerializer
from api.v1.serializers.exchange_rate import ExchangeRateSerializer, ActiveExchangeRateSerializer
from api.v1.serializers.lazylogin import LazyLoginSerializer
from api.v1.serializers.municipality import MunicipalitySerializer
from api.v1.serializers.province import ProvinceSerializer
from api.v1.serializers.telegram_group import TelegramGroupSerializer
from comohay import settings
from currencies.models import CurrencyAd
from currencies.models.exchange_rate import ExchangeRate
from utils.pagination import BasicSizePaginator
from utils.usd_value_helper import USDValueHelper
from django.db.models import Subquery, Max


class LazyLoginView(LoginView):
    serializer_class = LazyLoginSerializer

    def login(self):
        self.user = self.serializer.validated_data['user']

        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user,
                                      self.serializer)

        if getattr(settings, 'REST_SESSION_LOGIN', True):
            self.process_login()


class AdViewSet(viewsets.ModelViewSet):
    queryset = Ad.objects.all()
    serializer_class = AdSerializer
    filterset_fields = '__all__'
    pagination_class = BasicSizePaginator


class MunicipalityViewSet(viewsets.ModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    filterset_fields = [field.name for field in Municipality._meta.fields]
    # filterset_fields.append('province__name')
    pagination_class = BasicSizePaginator


class ProvinceViewSet(viewsets.ModelViewSet):
    queryset = Province.objects.all()
    serializer_class = ProvinceSerializer
    filterset_fields = [field.name for field in Province._meta.fields]
    filterset_fields.append('municipality__id')
    pagination_class = BasicSizePaginator


class AdSearchViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = AdSearchSerializer
    # permission_classes = (IsAuthenticated,)
    permission_classes = []

    # authentication_classes = (SessionAuthentication, BasicAuthentication)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('q', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING)
    ])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        request = self.request
        queryset = EmptySearchQuerySet()

        if request.GET.get('q') is not None:
            query = request.GET.get('q')
            queryset = SearchQuerySet().filter(content=query).highlight()

        return queryset


class USDValueView(APIView):
    """
    Retrieve, usd sale value, usd purchase value and general value.
    """
    permission_classes = [AllowAny]

    def get(self, request, days=7):
        return Response(USDValueHelper.get_avg_values(days), status=HTTP_200_OK)


class USDValueHistoryView(APIView):
    """
    Retrieve, usd value history
    """

    permission_classes = [AllowAny]

    def get(self, request, start, end, freq):
        return Response(USDValueHelper.get_history_values(start, end, freq), status=HTTP_200_OK)


class ExchangeRateView(APIView):
    """
    Retrieve the exchange rate for two given currencies, a etype("exchange type": buy, sell or mid rates) and a UTC
    datetime
    """

    permission_classes = [AllowAny]

    def get(self, request, source_currency_iso, target_currency_iso, etype=ExchangeRate.TYPE_BUY, target_datetime=None):

        if target_datetime is None:
            target_datetime = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        try:
            # just getting the newer exchange rate that is less than or equal to the target datetime
            exchange_rate = ExchangeRate.objects.filter(
                source_currency_iso=source_currency_iso,
                target_currency_iso=target_currency_iso,
                type=etype,
                datetime__lte=target_datetime
            ).order_by("-datetime")[0:1].get()

            return JsonResponse(ExchangeRateSerializer(exchange_rate).data)

        except ExchangeRate.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return HttpResponse(content=e, status=HTTP_422_UNPROCESSABLE_ENTITY)


# if I would want to add pagination just inherit from GenericAPIView, declare the serializer and uncomment the block
# starting with "PAGINATION"
class ExchangeRateHistoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, source_currency_iso, target_currency_iso, etype=ExchangeRate.TYPE_BUY, from_datetime=None,
            to_datetime=None):

        if from_datetime is None:
            from_datetime = (datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=30)).strftime(
                "%Y-%m-%d %H:%M:%S")

        if to_datetime is None:
            to_datetime = datetime.datetime.now(tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Here we get the latest exchange rates datetimes for every day. We group by the date part of the datetime and
        # then select the max datetime of the group
        latest_daily_er_datetimes = ExchangeRate.objects.filter(
            source_currency_iso=source_currency_iso,
            target_currency_iso=target_currency_iso,
            type=etype,
            datetime__gte=from_datetime,
            datetime__lte=to_datetime
        ).values("datetime__date").annotate(datetime=Max('datetime'))

        # Then we use here the previous datetimes(maximun datetimes for each day) to get its corresponding exchange rates
        exchange_rates = ExchangeRate.objects.filter(
            source_currency_iso=source_currency_iso,
            target_currency_iso=target_currency_iso,
            type=etype,
            datetime__in=Subquery(latest_daily_er_datetimes.values('datetime'))
        ).order_by("datetime")

        # PAGINATION
        # page = self.paginate_queryset(exchange_rates)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     return self.get_paginated_response(serializer.data)

        serializer = ExchangeRateSerializer(exchange_rates, many=True)
        return Response(serializer.data)


class CurrencyAdView(generics.ListAPIView):
    queryset = CurrencyAd.objects.filter(ad__is_deleted=False)
    serializer_class = CurrencyAdSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['type', 'source_currency_iso', 'target_currency_iso', 'ad__province__id',
                        'ad__municipality__id']
    ordering_fields = ['ad__external_created_at', 'price']
    ordering = ['-ad__external_created_at']


class TelegramGroupsView(generics.ListAPIView):
    queryset = TelegramGroup.objects.order_by('province_id')
    serializer_class = TelegramGroupSerializer
    pagination_class = None


class ClassifiedsPlatformsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        classifier_platforms = []
        for external_source_name, external_source_url in settings.EXTERNAL_SOURCES.items():
            classifier_platforms.append({"name": external_source_name, "url": external_source_url})
        return Response(ClassifiedsPlatformSerializer(classifier_platforms, many=True).data)


class ActiveExchangeRatesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, target_datetime_str=None):

        if target_datetime_str is None:
            target_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        else:
            target_datetime = datetime.datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=datetime.timezone.utc)

        active_exchange_rates = currencies.services.exchange_rate_service.get_active_exchange_rate_list(
            ref_type=ExchangeRate.TYPE_BUY,
            target_datetime=target_datetime
        )

        serializer = ActiveExchangeRateSerializer(active_exchange_rates, many=True)

        return Response(serializer.data)


class ActiveExchangeRateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, source_currency_iso, target_currency_iso, target_datetime_str=None):

        if target_datetime_str is None:
            target_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        else:
            target_datetime = datetime.datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=datetime.timezone.utc)

        active_exchange_rate = currencies.services.exchange_rate_service.get_active_exchange_rate(
            source_currency_iso=source_currency_iso,
            target_currency_iso=target_currency_iso,
            ref_type=ExchangeRate.TYPE_BUY,
            target_datetime=target_datetime
        )

        if not active_exchange_rate:
            return Response(HTTP_404_NOT_FOUND)

        serializer = ActiveExchangeRateSerializer(active_exchange_rate)

        return Response(serializer.data)
