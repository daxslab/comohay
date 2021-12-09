from typing import Union

from django.db.models import QuerySet, Q, Window, Max, F
from django.db.models.functions import RowNumber
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
    exchange_rates = compute_exchange_rates()

    for exchange_rate in exchange_rates:
        exchange_rate.save()

    return exchange_rates


def compute_exchange_rates(target_datetime: datetime.datetime = None):
    if target_datetime is None:
        target_datetime = datetime.datetime.now(tz=datetime.timezone.utc)

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


def get_active_exchange_rate(
        source_currency_iso,
        target_currency_iso,
        ref_type: str = ExchangeRate.TYPE_MID,
        target_datetime: datetime.datetime = None,
        limit_datetime: datetime.datetime = None,
):
    query = Q(source_currency_iso=source_currency_iso) & Q(target_currency_iso=target_currency_iso) & Q(type=ref_type)

    if target_datetime:
        query &= Q(datetime__lte=target_datetime)

    if limit_datetime:
        query &= Q(datetime__gte=limit_datetime)

    ref_exchange_rate = ExchangeRate.objects.filter(query).order_by('-datetime').first()

    if ref_exchange_rate is None:
        return None

    types_map = {
        ExchangeRate.TYPE_MID: 'mid_exchange_rate',
        ExchangeRate.TYPE_BUY: 'buy_exchange_rate',
        ExchangeRate.TYPE_SELL: 'sell_exchange_rate'
    }

    active_exchange_rate = ActiveExchangeRate(
        source_currency_iso=source_currency_iso,
        target_currency_iso=target_currency_iso,
        target_datetime=ref_exchange_rate.datetime
    )

    setattr(active_exchange_rate, types_map[ref_type], ref_exchange_rate)

    remaining_types = {ExchangeRate.TYPE_MID, ExchangeRate.TYPE_BUY, ExchangeRate.TYPE_SELL}.difference(ref_type)

    for rtype in remaining_types:
        # find the exchange rate in the same date and with an older or equal
        # datetime than the ref exchange rate, it can be none
        exchange_rate = ExchangeRate.objects.filter(
            source_currency_iso=source_currency_iso,
            target_currency_iso=target_currency_iso,
            type=rtype,
            datetime__date=ref_exchange_rate.datetime.date(),
            datetime__lte=ref_exchange_rate.datetime
        ).order_by('-datetime').first()

        if exchange_rate:
            setattr(active_exchange_rate, types_map[rtype], exchange_rate)

    return active_exchange_rate


def get_active_exchange_rate_list(
        ref_type: str = ExchangeRate.TYPE_MID,
        target_datetime: datetime.datetime = None,
        limit_datetime: datetime.datetime = None
):
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

    active_exchange_rate_list = []

    for target_currency_iso in target_currencies_isos:
        for source_currency_iso in source_currencies_isos:
            if target_currency_iso != source_currency_iso:
                active_exchange_rate = get_active_exchange_rate(
                    source_currency_iso,
                    target_currency_iso,
                    ref_type,
                    target_datetime,
                    limit_datetime
                )
                if active_exchange_rate:
                    active_exchange_rate_list.append(active_exchange_rate)

    return active_exchange_rate_list


# This method is not in use right now, but I leave it here for future reference using windows functions
def get_newest_exchange_rates_queryset(
        source_currency_iso=None,
        target_currency_iso=None,
        etype=None,
        from_datetime: datetime.datetime = None,
        to_datetime: datetime.datetime = None
) -> QuerySet:
    """
    Returns the newest exchange rates in the groups defined by the fields source_currency_iso,
    target_currency_iso and etype which are older than the to_datetime param and newer than from_datetime.
    The returned QuerySet is also filtered by the params source_currency_iso, target_currency_iso and etype
    :param source_currency_iso:
    :param target_currency_iso:
    :param etype:
    :param target_datetime:
    :param limit_datetime:
    :return: QuerySet of ExchangeRate(s)
    """

    query = Q()

    if source_currency_iso:
        query &= Q(source_currency_iso=source_currency_iso)

    if target_currency_iso:
        query &= Q(target_currency_iso=target_currency_iso)

    if etype:
        query &= Q(etype=etype)

    if from_datetime:
        query &= Q(datetime_gte=from_datetime)

    if to_datetime:
        query &= Q(datetime_lte=to_datetime)

    exchange_rates_queryset = ExchangeRate.objects.filter(query).annotate(
        rank=Window(
            expression=RowNumber(),
            partition_by=[F('source_currency_iso'), F('target_currency_iso'), F('etype')],
            order_by=F('datetime').desc()
        )
    ).filter(rank=1)

    return exchange_rates_queryset


def get_open_exchange_rate_of(exchange_rate: ExchangeRate) -> Union[ExchangeRate, None]:
    week_day = exchange_rate.datetime.weekday()
    open_date = exchange_rate.datetime.date() - datetime.timedelta(days=week_day)

    open_exchange_rate = ExchangeRate.objects.filter(
        source_currency_iso=exchange_rate.source_currency_iso,
        target_currency_iso=exchange_rate.target_currency_iso,
        type=exchange_rate.type,
        datetime__gte=open_date
    ).order_by('datetime').first()

    return open_exchange_rate


def get_52_week_high_exchange_rate_of(exchange_rate: ExchangeRate) -> Union[ExchangeRate, None]:
    return ExchangeRate.objects.filter(
        source_currency_iso=exchange_rate.source_currency_iso,
        target_currency_iso=exchange_rate.target_currency_iso,
        type=exchange_rate.type,
        datetime__year=exchange_rate.datetime.year,
        datetime__lte=exchange_rate.datetime
    ).order_by('-wavg').first()


def get_52_week_low_exchange_rate_of(exchange_rate: ExchangeRate) -> Union[ExchangeRate, None]:
    return ExchangeRate.objects.filter(
        source_currency_iso=exchange_rate.source_currency_iso,
        target_currency_iso=exchange_rate.target_currency_iso,
        type=exchange_rate.type,
        datetime__year=exchange_rate.datetime.year,
        datetime__lte=exchange_rate.datetime
    ).order_by('wavg').first()
