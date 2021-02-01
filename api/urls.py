from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api import views
from api.views import AdViewSet, ProvinceViewSet, MunicipalityViewSet, AdSearchViewSet, USDValueView, \
    USDValueHistoryView

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
    url(r'^rest-auth/', include('rest_auth.urls')),
    url('rest-auth/lazy-login', views.LazyLoginView.as_view(), name='lazy_login'),
    path('usd-value/<int:days>/', USDValueView.as_view()),
    path('usd-value/', USDValueView.as_view()),
    path('usd-value-history/<str:start>/<str:end>/<str:batch>', USDValueHistoryView.as_view()),
]
