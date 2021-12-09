from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from api.v2.views import ActiveExchangeRatesView, ActiveExchangeRateView, OpenExchangeRateView, \
    FiftyTwoWeekHighExchangeRateView, FiftyTwoWeekLowExchangeRateView

app_name = 'apiv2'

schema_view = get_schema_view(
    openapi.Info(
        title="ComoHay API",
        default_version='v2',
    ),
    public=True,
    permission_classes=tuple([permissions.AllowAny]),
)

urlpatterns = [
    path('currencies/active-exchange-rates/', ActiveExchangeRatesView.as_view()),
    path(
        'currencies/active-exchange-rates/<str:source_currency_iso>/<str:target_currency_iso>/',
        ActiveExchangeRateView.as_view()
    ),
    path('currencies/exchange-rates/<int:id>/open-exchange-rate', OpenExchangeRateView.as_view()),
    path('currencies/exchange-rates/<int:id>/52-week-high-exchange-rate', FiftyTwoWeekHighExchangeRateView.as_view()),
    path('currencies/exchange-rates/<int:id>/52-week-low-exchange-rate', FiftyTwoWeekLowExchangeRateView.as_view())
]
