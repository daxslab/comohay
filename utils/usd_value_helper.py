from urllib.parse import urlencode
import io
import pandas as pd
import numpy as np
from pandas import DataFrame
from scipy import stats
import pytz
import requests
from urllib.parse import urlencode
import re


class USDValueHelper:

    # please never use here the verb "tener" or any of its conjugations, surprisingly the verb is an stop word in
    # the file solr/solr_config/conf/lang/stopwords_es.txt therefore it's removed from every query
    sale_phrase_queries = [
        "vendo dolares", "vendo usd", "vendo dolares americanos", "venta de dolares", "venta de usd",
        "en venta usd", "se venden dolares", "se vende USD", "dolares en venta", "usd en venta"
    ]

    purchase_phrase_queries = [
        "compro dolares", "compro usd", "compro dolares americanos", "compra de dolares", "compra de usd",
        "en compra usd", "se compran dolares", "se compra USD", "dolares en compra", "usd en compra", "necesito usd",
        "necesito dolares", "busco dolares", "busco usd"
    ]

    solr_base_params = {
        'defType': 'edismax',
        # filter query
        # query field
        'qf': 'title',
        # phrase field
        'pf': 'title',
        # query slop
        'qs': 2,
        'start': 0,
        'rows': 2147483647,
        'wt': 'csv'
    }

    @staticmethod
    def get_avg_values(days=7):
        """
            Retrieve, usd avg sale value, usd avg purchase value and avg general value.
        """
        params = USDValueHelper.solr_base_params
        params['fq'] = 'external_created_at:[NOW-{}DAY TO NOW]'.format(days)

        params['q'] = '\"' + '\" OR \"'.join(USDValueHelper.sale_phrase_queries) + '\"'
        sale_query = 'http://solr:8983/solr/ads/select/?' + urlencode(params)
        sale_data = USDValueHelper.process_avg_value_query(sale_query)

        params['q'] = '\"' + '\" OR \"'.join(USDValueHelper.purchase_phrase_queries) + '\"'
        purchase_query = 'http://solr:8983/solr/ads/select/?' + urlencode(params)
        purchase_data = USDValueHelper.process_avg_value_query(purchase_query)

        all_data = pd.concat([sale_data, purchase_data])

        return {
            "saleValue": {
                "avgValue": sale_data['price'].mean(),
                "maxValue": sale_data['price'].max(),
                "minValue": sale_data['price'].min(),
                "adsQty": len(sale_data)
            },
            "purchaseValue": {
                "avgValue": purchase_data['price'].mean(),
                "maxValue": purchase_data['price'].max(),
                "minValue": purchase_data['price'].min(),
                "adsQty": len(purchase_data)
            },
            "generalValue": {
                "avgValue": all_data['price'].mean(),
                "maxValue": all_data['price'].max(),
                "minValue": all_data['price'].min(),
                "adsQty": len(all_data)
            }
        }

    @staticmethod
    def process_avg_value_query(query: str):
        response = requests.get(query)
        data = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        data = USDValueHelper.standardizing_prices(data)
        data = USDValueHelper.removing_outliers(data)
        return data

    @staticmethod
    def standardizing_prices(data: DataFrame):
        for index, row in data.iterrows():
            if 1 <= row['price'] <= 10:
                row['price'] = row['price'] * 25
            elif not row['price']:
                match = re.search('(a|en) (?P<price>\d+([.,]\d+)?)', row['title'])
                if match is not None:
                    row['price'] = float(match.group('price').replace(',', '.'))
                else:
                    data.drop(index=index)
        return data

    @staticmethod
    def removing_outliers(data: DataFrame):
        # cleaning anomalous values
        data = data[(data.price > 0) & (data.price <= 250)]
        # data = data[((data.price >= 1) & (data.price <= 10)) | ((data.price >= 24) & (data.price <= 250))]

        # removing price outliers,
        # refer to https://stackoverflow.com/questions/23199796/detect-and-exclude-outliers-in-pandas-data-frame
        data = data[(np.abs(stats.zscore(data['price'])) < 2)]
        return data