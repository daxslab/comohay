from scipy import stats
import pandas as pd
import numpy as np
import datetime
from ads.models import Ad
from currencies.models import CurrencyAd
from currencies.models.exchange_rate import ExchangeRate

# an ad can't be older than this value
days_span = 7
min_number_of_ads_for_an_exchange_rate = days_span
max_mzscore = 2

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

                # recovering the last exchange rate in order to use its wavg as the mean to compute the standard
                # deviation
                # last_exchange_rate = ExchangeRate.objects.filter(
                #     source_currency_iso=source_currency_iso,
                #     target_currency_iso=target_currency_iso,
                #     type=exchange_rate_type,
                #     datetime__lte=target_datetime,
                #     datetime__gte=(target_datetime - datetime.timedelta(days=7))
                # ).order_by("-datetime").first()

                # removing price outliers,
                # refer to https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame
                # see also https://math.stackexchange.com/questions/275836/what-is-difference-between-standard-deviation-and-z-score
                # if last_exchange_rate is None:
                #     # Computing z-sore in the usual way, using standard deviation from the sample mean
                #     currencyads_df = currencyads_df[(np.abs(stats.zscore(currencyads_df['price'])) <= 1)]
                #     std = currencyads_df['price'].std()
                # else:
                #     # Computing the z-score using the standard deviation(std) computed from the mean passed as argument,
                #     # which should be
                #     # the latest exchange rate
                #     mean = last_exchange_rate.wavg
                #     std = math.sqrt(np.sum(((currencyads_df["price"] - mean) ** 2)) / currencyads_df.shape[0])
                #     currencyads_df = currencyads_df[(np.abs((currencyads_df["price"] - mean) / std) <= max_zscore)]

                # removing outliers using a modified Z-scores M, a lot more robust for small datasets
                # see https://stats.stackexchange.com/questions/78609/outlier-detection-in-very-small-sets and
                # https://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm
                mad = stats.median_abs_deviation(currencyads_df['price'])
                median = currencyads_df['price'].median()
                mzscores = np.abs(.6745 * (currencyads_df['price'] - median) / mad)
                currencyads_df = currencyads_df[mzscores <= max_mzscore]

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
                    max_mzscore=max_mzscore,
                    ads_qty=len(currencyads_df),
                    datetime=target_datetime
                )

                exchange_rates.append(exchange_rate)

    return exchange_rates