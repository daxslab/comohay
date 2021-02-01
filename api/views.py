from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from haystack.query import EmptySearchQuerySet, SearchQuerySet
from rest_auth.app_settings import create_token
from rest_auth.utils import jwt_encode
from rest_auth.views import LoginView
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province
from api.models.ad import AdSerializer
from api.models.adsearch import AdSearchSerializer
from api.models.lazylogin import LazyLoginSerializer
from api.models.municipality import MunicipalitySerializer
from api.models.province import ProvinceSerializer
from comohay import settings
from utils.pagination import BasicSizePaginator
from utils.usd_value_helper import USDValueHelper


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
