from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from api.views import AdViewSet, ProvinceViewSet, MunicipalityViewSet, AdSearchViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'provinces', ProvinceViewSet)
router.register(r'municipalities', MunicipalityViewSet)
router.register(r'search', AdSearchViewSet, basename='search')

urlpatterns = [
    url('^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls'))
]