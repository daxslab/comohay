import datetime

from ads.models import Ad
from currencies.models import ExchangeRate
from currencies.models.exchange_rate import ActiveExchangeRate


def get_active_exchange_rate(source_currency_iso, target_currency_iso, target_datetime: datetime.datetime = None):
    if target_datetime is None:
        target_datetime = datetime.datetime.now(tz=datetime.timezone.utc)

    buy_exchange_rate = ExchangeRate.objects.filter(
        source_currency_iso=source_currency_iso,
        target_currency_iso=target_currency_iso,
        type=ExchangeRate.TYPE_BUY,
        datetime__lte=target_datetime
    ).order_by('-datetime').first()

    if buy_exchange_rate is None:
        return None

    # find the mid exchange rate with the same datetime than the
    # buy exchange rate (there must be always one)
    mid_exchange_rate = ExchangeRate.objects.filter(
        source_currency_iso=source_currency_iso,
        target_currency_iso=target_currency_iso,
        type=ExchangeRate.TYPE_MID,
        datetime=buy_exchange_rate.datetime
    ).order_by('-datetime').first()

    # find the sell rate in the same date and older or equal
    # datetime than the buy rate, it can be none
    sell_exchange_rate = ExchangeRate.objects.filter(
        source_currency_iso=source_currency_iso,
        target_currency_iso=target_currency_iso,
        type=ExchangeRate.TYPE_SELL,
        datetime__date=buy_exchange_rate.datetime.date(),
        datetime__lte=buy_exchange_rate.datetime
    ).order_by('-datetime').first()

    active_exchange_rate = ActiveExchangeRate(
        source_currency_iso=source_currency_iso,
        target_currency_iso=target_currency_iso,
        buy_exchange_rate=buy_exchange_rate,
        sell_exchange_rate=sell_exchange_rate,
        mid_exchange_rate=mid_exchange_rate,
        target_datetime=buy_exchange_rate.datetime
    )

    return active_exchange_rate


def get_active_exchange_rates(target_datetime: datetime.datetime = None):
    if target_datetime is None:
        target_datetime = datetime.datetime.now(tz=datetime.timezone.utc)

    # setting a custom order
    source_currencies_isos = [Ad.AMERICAN_DOLLAR_ISO, Ad.MLC_ISO, Ad.EURO_ISO]

    # Excluding CUP, CUC and the previous inserted currencies from source currencies
    for currency in Ad.ALLOWED_CURRENCIES:
        if currency[0] not in (
                Ad.CONVERTIBLE_CUBAN_PESO_ISO, Ad.CUBAN_PESO_ISO, Ad.EURO_ISO, Ad.MLC_ISO, Ad.AMERICAN_DOLLAR_ISO):
            source_currencies_isos.append(currency[0])

    # setting a custom order
    target_currencies_isos = [Ad.CUBAN_PESO_ISO, Ad.AMERICAN_DOLLAR_ISO, Ad.MLC_ISO, Ad.EURO_ISO]

    # Excluding CUC and the previous inserted currencies from target currencies
    for currency in Ad.ALLOWED_CURRENCIES:
        if currency[0] not in (
                Ad.CONVERTIBLE_CUBAN_PESO_ISO, Ad.CUBAN_PESO_ISO, Ad.EURO_ISO, Ad.MLC_ISO, Ad.AMERICAN_DOLLAR_ISO):
            target_currencies_isos.append(currency[0])

    active_exchange_rates = []

    for target_currency_iso in target_currencies_isos:
        for source_currency_iso in source_currencies_isos:
            if target_currency_iso != source_currency_iso:
                active_exchange_rate = get_active_exchange_rate(source_currency_iso, target_currency_iso,
                                                                target_datetime)
                if active_exchange_rate:
                    active_exchange_rates.append(active_exchange_rate)

    return active_exchange_rates
