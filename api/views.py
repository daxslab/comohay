from django.core.exceptions import ValidationError
from django.http import JsonResponse, HttpResponse
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
from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province
from api.models.ad import AdSerializer
from api.models.adsearch import AdSearchSerializer
from api.models.currencyad import CurrencyAdSerializer
from api.models.exchange_rate import ExchangeRateSerializer
from api.models.lazylogin import LazyLoginSerializer
from api.models.municipality import MunicipalitySerializer
from api.models.province import ProvinceSerializer
from comohay import settings
from currencies.models import CurrencyAd
from currencies.models.exchange_rate import ExchangeRate
from utils.pagination import BasicSizePaginator
from utils.usd_value_helper import USDValueHelper
import datetime
from django.db.models import Subquery, Max, F, Func


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
            # just getting the older exchange rate that is less than or equal to the target datetime
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


class ExchangeRateCurrencyAdView(APIView):
    """
    View to retrieve the currency ads used to compute the last exchange rate relative to the datetime passed as argument
    """

    permission_classes = [AllowAny]

    def get(self, request, source_currency_iso, target_currency_iso, currencyad_type, target_datetime_str=None):

        if target_datetime_str is None:
            target_datetime = datetime.datetime.now(tz=datetime.timezone.utc)
        else:
            target_datetime = datetime.datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=datetime.timezone.utc)

        exchange_rate_type = ExchangeRate.TYPE_BUY
        currencyad_type_filter = [currencyad_type]

        if currencyad_type == CurrencyAd.TYPE_PURCHASE:
            exchange_rate_type = ExchangeRate.TYPE_SELL
        elif currencyad_type == 'all':
            exchange_rate_type = ExchangeRate.TYPE_MID
            currencyad_type_filter = [CurrencyAd.TYPE_SALE, CurrencyAd.TYPE_PURCHASE]

        last_exchange_rate = ExchangeRate.objects.filter(
            source_currency_iso=source_currency_iso,
            target_currency_iso=target_currency_iso,
            type=exchange_rate_type,
            datetime__lte=target_datetime
        ).order_by("-datetime").first()

        if last_exchange_rate is None:
            return Response(HTTP_404_NOT_FOUND)

        mzscore_func = Func(.6745 * (F('price') - last_exchange_rate.median) / last_exchange_rate.mad, function='ABS')
        currencyad_qs = CurrencyAd.objects.annotate(mzscore=mzscore_func).filter(
            source_currency_iso=source_currency_iso,
            target_currency_iso=target_currency_iso,
            type__in=currencyad_type_filter,
            ad__external_created_at__lte=last_exchange_rate.datetime,
            ad__external_created_at__gte=last_exchange_rate.datetime - datetime.timedelta(last_exchange_rate.days_span),
            # TODO: add condition to filter by is_deleted and by deleted_at
            mzscore__lte=last_exchange_rate.max_mzscore
        )

        serializer = CurrencyAdSerializer(currencyad_qs, many=True)
        return Response(serializer.data)
