from django.conf.urls import url
from django.urls import include, path
from rest_framework import routers, permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from api import views
from api.views import AdViewSet, ProvinceViewSet, MunicipalityViewSet, AdSearchViewSet, USDValueView, \
    USDValueHistoryView, ExchangeRateView, ExchangeRateHistoryView, CurrencyAdView, ActiveExchangeRatesView, \
    ActiveExchangeRateView, ClassifiedsPlatformsView, TelegramGroupsView

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
    path('usd-value-history/<str:start>/<str:end>/<str:freq>', USDValueHistoryView.as_view()),
    path('usd-value-history/<str:start>/<str:end>/<str:freq>', USDValueHistoryView.as_view()),
    path('usd-value-history/<str:start>/<str:end>/<str:freq>', USDValueHistoryView.as_view()),
    path(
        'currencies/exchange-rate/<str:source_currency_iso>/<str:target_currency_iso>/<str:etype>/<str:target_datetime>',
        ExchangeRateView.as_view()
        ),
    path(
        'currencies/exchange-rate-history/<str:source_currency_iso>/<str:target_currency_iso>/<str:etype>/<str:from_datetime>/<str:to_datetime>',
        ExchangeRateHistoryView.as_view()
    ),
    path('currencies/active-exchange-rates/<str:target_datetime_str>', ActiveExchangeRatesView.as_view()),
    path('currencies/active-exchange-rates', ActiveExchangeRatesView.as_view()),
    path(
        'currencies/active-exchange-rates/<str:source_currency_iso>/<str:target_currency_iso>/<str:target_datetime_str>',
        ActiveExchangeRateView.as_view()
    ),
    path(
        'currencies/active-exchange-rates/<str:source_currency_iso>/<str:target_currency_iso>/',
        ActiveExchangeRateView.as_view()
    ),
    path('currencies/currencyads/', CurrencyAdView.as_view()),
    path('classifieds-platforms', ClassifiedsPlatformsView.as_view()),
    path('telegram-groups', TelegramGroupsView.as_view())
]
