import django_filters
from django_filters.rest_framework import FilterSet
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province
from api.models.ad import AdSerializer
from api.models.municipality import MunicipalitySerializer
from api.models.province import ProvinceSerializer
from utils.pagination import BasicSizePaginator


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
