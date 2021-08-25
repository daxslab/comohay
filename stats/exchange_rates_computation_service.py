from pandas import DataFrame
from urllib.parse import urlencode
from scipy import stats
import requests
import pandas as pd
import io
import re
import numpy as np
import datetime
from stats.models.exchange_rate import ExchangeRate
import pytz
import math

# an ad can't be older than this value
days_limit = 7

solr_base_path = 'http://solr:8983/solr/ads/select'

solr_base_params = {
    'defType': 'edismax',
    # query field
    'qf': 'title',
    # phrase field
    'pf': 'title',
    # query slop
    'qs': 2,
    'start': 0,
    'rows': 2147483647,
    # specifies the Response Writer to be used to format the query response.
    'wt': 'csv'
}

# please never use here the verb "tener" or any of its conjugations, surprisingly the verb is an stop word in
# the file solr/solr_config/conf/lang/stopwords_es.txt therefore it's removed from every query
base_sale_phrase_queries = [
    "vendo {singular}", "vendo {plural}", "vendo {iso}",
    "venta de {singular}", "venta de {plural}", "venta de {iso}",
    "en venta {singular}", "en venta {plural}", "en venta {iso}",
    "se vende {singular}", "se venden {plural}", "se vende {iso}",
    "{singular} en venta", "{plural} en venta", "{iso} en venta"
]

base_purchase_phrase_queries = [
    "compro {singular}", "compro {plural}", "compro {iso}",
    "compra de {singular}", "compra de {plural}", "compra de {iso}",
    "en compra {singular}", "en compra {plural}", "en compra {iso}",
    "se compra {singular}", "se compran {plural}", "se compra {iso}",
    "{singular} en compra", "{plural} en compra", "{iso} en compra",
    "necesito {singular}", "necesito {plural}", "necesito {iso}",
    "necesito comprar {singular}", "necesito comprar {plural}", "necesito comprar {iso}",
    "busco {singular}", "busco {plural}", "busco {iso}"
]

usd_sale_extra_phrase_queries = ["vendo dolares americanos"]
usd_purchase_extra_phrase_queries = ["compro dolares americanos"]


def get_phrase_queries():
    eur_sale_phrase_queries = [phrase.format(singular="euro", plural="euros", iso="EUR") for phrase in
                               base_sale_phrase_queries]

    eur_purchase_phrase_queries = [phrase.format(singular="euro", plural="euros", iso="EUR") for phrase in
                                   base_purchase_phrase_queries]

    usd_sale_phrase_queries = [phrase.format(singular="dólar", plural="dólares", iso="USD") for phrase in
                               base_sale_phrase_queries] + usd_sale_extra_phrase_queries

    usd_purchase_phrase_queries = [phrase.format(singular="dólar", plural="dólares", iso="USD") for phrase in
                                   base_purchase_phrase_queries] + usd_purchase_extra_phrase_queries

    mlc_sale_phrase_queries = [phrase.format(singular="mlc", plural="mlc", iso="MLC") for phrase in
                               base_sale_phrase_queries]

    mlc_purchase_phrase_queries = [phrase.format(singular="mlc", plural="mlc", iso="MLC") for phrase in
                                   base_purchase_phrase_queries]
    return {
        "EUR": {
            ExchangeRate.TYPE_BUY: eur_sale_phrase_queries,
            ExchangeRate.TYPE_SELL: eur_purchase_phrase_queries,
            ExchangeRate.TYPE_MID: eur_sale_phrase_queries + eur_purchase_phrase_queries
        },
        "USD": {
            ExchangeRate.TYPE_BUY: usd_sale_phrase_queries,
            ExchangeRate.TYPE_SELL: usd_purchase_phrase_queries,
            ExchangeRate.TYPE_MID: usd_sale_phrase_queries + usd_purchase_phrase_queries
        },
        "MLC": {
            ExchangeRate.TYPE_BUY: mlc_sale_phrase_queries,
            ExchangeRate.TYPE_SELL: mlc_purchase_phrase_queries,
            ExchangeRate.TYPE_MID: mlc_sale_phrase_queries + mlc_purchase_phrase_queries
        }
    }


def update_exchange_rates():
    exchange_rates = get_exchange_rates()

    for exchange_rate in exchange_rates:
        exchange_rate.save()

    return exchange_rates


def get_exchange_rates(target_datetime: datetime.datetime = datetime.datetime.now(tz=datetime.timezone.utc)):
    params = solr_base_params

    # filter query
    params['fq'] = "external_created_at:[{now}-{days}DAY TO {now}]".format(
        now=target_datetime.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), days=days_limit)

    exchange_rates = []

    for currency_iso, phrases_values in get_phrase_queries().items():
        for exchange_type, phrases in phrases_values.items():

            params['q'] = '\"' + '\" OR \"'.join(phrases) + '\"'
            response = requests.get(solr_base_path + "/?{}".format(urlencode(params)))

            ads_dataframe = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
            ads_dataframe = standardize_prices(ads_dataframe)

            # recovering the last exchange rate
            last_exchange_rate = ExchangeRate.objects.filter(
                source_currency_iso=currency_iso,
                target_currency_iso="CUP",
                type=exchange_type,
                datetime__lte=target_datetime,
                datetime__gte=(target_datetime - datetime.timedelta(days=7))
            ).order_by("-datetime").first()

            if last_exchange_rate is None:
                ads_dataframe = remove_price_outliers(ads_dataframe)
            else:
                ads_dataframe = remove_price_outliers(ads_dataframe, float(last_exchange_rate.wavg))

            # if there is no ads left after the pre-processing then ignore the current exchange type
            if not any(ads_dataframe['price']):
                continue

            # computing Weighted Mean: https://en.wikipedia.org/wiki/Weighted_arithmetic_mean. The weight is a
            # reciprocal function applied to the difference in days between the current date and the ad date
            def reciprocal(ad_datetime_str):
                ad_datetime_str = datetime.datetime.fromisoformat(ad_datetime_str.replace('Z', '+00:00'))
                days_diff = (target_datetime - ad_datetime_str).days
                return 1 / (0.1 * days_diff + 1)

            wavg = np.average(ads_dataframe['price'], weights=[reciprocal(row['external_created_at']) for index, row in
                                                               ads_dataframe.iterrows()])
            maxp = ads_dataframe['price'].max()
            minp = ads_dataframe['price'].min()

            exchange_rate = ExchangeRate(
                source_currency_iso=currency_iso,
                target_currency_iso="CUP",
                type=exchange_type,
                wavg=wavg,
                max=maxp,
                min=minp,
                ads_qty=len(ads_dataframe),
                datetime=target_datetime
            )

            exchange_rates.append(exchange_rate)

    return exchange_rates


def standardize_prices(data: DataFrame):
    for index in data.index:

        price_match = re.search('(a|en) (?P<price>\d+([.,]\d+)?)', data.at[index, 'title'])
        if price_match:
            data.at[index, 'price'] = float(price_match.group('price').replace(',', '.'))

        if not data.at[index, 'price']:
            data.drop(index=index)

        if 1 <= data.at[index, 'price'] <= 10:
            if data.at[index, 'external_created_at'] < '2021-04-01':
                data.at[index, 'price'] = data.at[index, 'price'] * 25
            else:
                data.drop(index=index)

    return data


def remove_price_outliers(data: DataFrame, mean=None):
    # cleaning anomalous values
    data = data[(data.price > 0) & (data.price <= 250)]
    # data = data[((data.price >= 1) & (data.price <= 10)) | ((data.price >= 24) & (data.price <= 250))]

    # removing price outliers,
    # refer to https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame
    # see also https://math.stackexchange.com/questions/275836/what-is-difference-between-standard-deviation-and-z-score

    if mean is None:
        # Computing z-sore in the usual way, using standard deviation from the sample mean
        return data[(np.abs(stats.zscore(data['price'])) <= 1)]

    # Computing the z-score using the standard deviation(std) computed from the mean passed as argument, which should be
    # the latest exchange rate
    std = math.sqrt(np.sum(((data["price"] - mean) ** 2)) / data.shape[0])
    return data[(np.abs((data["price"] - mean) / std) <= 1)]
