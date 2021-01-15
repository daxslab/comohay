from django.conf.urls import url
from django.urls import include
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api.views import AdViewSet, ProvinceViewSet, MunicipalityViewSet, AdSearchViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'provinces', ProvinceViewSet)
router.register(r'municipalities', MunicipalityViewSet)
router.register(r'search', AdSearchViewSet, basename='search')


schema_view = get_schema_view(
   openapi.Info(
      title="ComoHay API",
      default_version='v1',
      # description="Test description",
      # terms_of_service="https://www.google.com/policies/terms/",
      # contact=openapi.Contact(email="contact@snippets.local"),
      # license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    url('^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls'))
]