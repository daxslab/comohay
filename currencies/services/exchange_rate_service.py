from scipy import stats
import pandas as pd
import numpy as np
import datetime
from ads.models import Ad
from currencies.models import CurrencyAd
from currencies.models.exchange_rate import ExchangeRate, ActiveExchangeRate

# an ad can't be older than this value
days_span = 3
min_number_of_ads_for_an_exchange_rate = 10
deviation_threshold = 2

exchange_rate_type_to_currency_ad_type_map = {
    ExchangeRate.TYPE_BUY: [CurrencyAd.TYPE_SALE],
    ExchangeRate.TYPE_SELL: [CurrencyAd.TYPE_PURCHASE],
    ExchangeRate.TYPE_MID: [CurrencyAd.TYPE_SALE, CurrencyAd.TYPE_PURCHASE],
}


def update_exchange_rates():
    exchange_rates = get_exchange_rates()

    for exchange_rate in exchange_rates:
        exchange_rate.save()

    return exchange_rates


def get_exchange_rates(target_datetime: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)):
    exchange_rates = []

    # Excluding CUP and CUC (we don't have this currency in curerncyads table) from source currencies
    source_currencies_isos = [currency[0] for currency in Ad.ALLOWED_CURRENCIES if
                              currency[0] not in (Ad.CONVERTIBLE_CUBAN_PESO_ISO, Ad.CUBAN_PESO_ISO)]

    # Excluding CUC (we don't have this currency in curerncyads table) from target currencies
    target_currencies_isos = [currency[0] for currency in Ad.ALLOWED_CURRENCIES if
                              currency[0] != Ad.CONVERTIBLE_CUBAN_PESO_ISO]

    for source_currency_iso in source_currencies_isos:
        for target_currency_iso in target_currencies_isos:

            if source_currency_iso == target_currency_iso:
                continue

            for exchange_rate_type, exchange_rate_type_name in ExchangeRate.TYPES:

                currencyad_queryset = CurrencyAd.objects.filter(
                    source_currency_iso=source_currency_iso,
                    target_currency_iso=target_currency_iso,
                    type__in=exchange_rate_type_to_currency_ad_type_map[exchange_rate_type],
                    ad__external_created_at__lte=target_datetime,
                    ad__external_created_at__gte=(target_datetime - datetime.timedelta(days=days_span))
                )

                # excluding currencyads who were deleted in the target period of time
                currencyad_queryset = currencyad_queryset.exclude(
                    ad__is_deleted=True,
                    ad__deleted_at__lt=target_datetime
                )

                if currencyad_queryset.count() == 0:
                    continue

                currencyads_df = pd.DataFrame(list(currencyad_queryset.values(
                    'id',
                    'source_currency_iso',
                    'target_currency_iso',
                    'type',
                    'price',
                    'ad__external_created_at'
                )))

                # removing outliers using the median absolute deviation
                # see https://core.ac.uk/download/pdf/206095228.pdf
                #
                # And optionally see:
                #   https://stats.stackexchange.com/questions/78609/outlier-detection-in-very-small-sets and
                #   https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm

                mad = stats.median_abs_deviation(x=currencyads_df['price'], scale='normal')
                median = currencyads_df['price'].median()
                max_deviation = deviation_threshold * mad
                currencyads_df = currencyads_df[(currencyads_df['price'] >= median - max_deviation) &
                                                (currencyads_df['price'] <= median + max_deviation)]


                # if there is no ads left after the pre-processing then ignore the current exchange type
                if currencyads_df.shape[0] < min_number_of_ads_for_an_exchange_rate:
                    continue

                # computing Weighted Mean: https://en.wikipedia.org/wiki/Weighted_arithmetic_mean. The weight is a
                # reciprocal function applied to the difference in days between the current date and the ad date
                def reciprocal(currencyad_datetime):
                    days_diff = (target_datetime - currencyad_datetime).days
                    return 1 / (0.1 * days_diff + 1)

                wavg = np.average(
                    a=currencyads_df['price'],
                    weights=[reciprocal(row['ad__external_created_at']) for index, row in currencyads_df.iterrows()]
                )
                maxp = currencyads_df['price'].max()
                minp = currencyads_df['price'].min()

                exchange_rate = ExchangeRate(
                    source_currency_iso=source_currency_iso,
                    target_currency_iso=target_currency_iso,
                    type=exchange_rate_type,
                    wavg=wavg,
                    max=maxp,
                    min=minp,
                    mad=mad,
                    median=median,
                    days_span=days_span,
                    deviation_threshold=deviation_threshold,
                    ads_qty=len(currencyads_df),
                    datetime=target_datetime
                )

                exchange_rates.append(exchange_rate)

    return exchange_rates


def get_active_exchange_rate(source_currency_iso, target_currency_iso, target_datetime: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)):

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


def get_active_exchange_rates(target_datetime: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)):

    # setting a custom order
    source_currencies_isos = [Ad.EURO_ISO, Ad.MLC_ISO, Ad.AMERICAN_DOLLAR_ISO]

    # Excluding CUP, CUC and the previous inserted currencies from source currencies
    for currency in Ad.ALLOWED_CURRENCIES:
        if currency[0] not in (Ad.CONVERTIBLE_CUBAN_PESO_ISO, Ad.CUBAN_PESO_ISO, Ad.EURO_ISO, Ad.MLC_ISO, Ad.AMERICAN_DOLLAR_ISO):
            source_currencies_isos.append(currency[0])

    # setting a custom order
    target_currencies_isos = [Ad.CUBAN_PESO_ISO, Ad.EURO_ISO, Ad.MLC_ISO, Ad.AMERICAN_DOLLAR_ISO]

    # Excluding CUC and the previous inserted currencies from target currencies
    for currency in Ad.ALLOWED_CURRENCIES:
        if currency[0] not in (Ad.CONVERTIBLE_CUBAN_PESO_ISO, Ad.CUBAN_PESO_ISO, Ad.EURO_ISO, Ad.MLC_ISO, Ad.AMERICAN_DOLLAR_ISO):
            target_currencies_isos.append(currency[0])

    active_exchange_rates = []

    for target_currency_iso in target_currencies_isos:
        for source_currency_iso in source_currencies_isos:
            active_exchange_rate = get_active_exchange_rate(source_currency_iso, target_currency_iso, target_datetime)
            if active_exchange_rate:
                active_exchange_rates.append(active_exchange_rate)

    return active_exchange_rates
