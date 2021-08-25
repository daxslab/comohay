import io
from datetime import datetime

import pandas as pd
import requests
from urllib.parse import urlencode
import stats.exchange_rates_computation_service


class USDValueHelper:
    solr_base_path = 'http://solr:8983/solr/ads/select'

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

        # getting and pre processing sale data
        params['q'] = '\"' + '\" OR \"'.join(USDValueHelper.sale_phrase_queries) + '\"'
        sale_response = USDValueHelper.solr_request(params)
        sale_data = pd.read_csv(io.StringIO(sale_response.content.decode('utf-8')))
        sale_data = stats.exchange_rates_computation_service.standardize_prices(sale_data)
        sale_data = stats.exchange_rates_computation_service.remove_price_outliers(sale_data)

        # getting and pre processing purchase data
        params['q'] = '\"' + '\" OR \"'.join(USDValueHelper.purchase_phrase_queries) + '\"'
        purchase_response = USDValueHelper.solr_request(params)
        purchase_data = pd.read_csv(io.StringIO(purchase_response.content.decode('utf-8')))
        purchase_data = stats.exchange_rates_computation_service.standardize_prices(purchase_data)
        purchase_data = stats.exchange_rates_computation_service.remove_price_outliers(purchase_data)

        all_data = pd.concat([sale_data, purchase_data])

        return {
            "saleValue": {
                "avgValue": sale_data['price'].mean() if any(sale_data['price']) else 0,
                "maxValue": sale_data['price'].max() if any(sale_data['price']) else 0,
                "minValue": sale_data['price'].min() if any(sale_data['price']) else 0,
                "adsQty": len(sale_data),
                "date": datetime.now().strftime('%Y-%m-%d')
            },
            "purchaseValue": {
                "avgValue": purchase_data['price'].mean() if any(purchase_data['price']) else 0,
                "maxValue": purchase_data['price'].max() if any(purchase_data['price']) else 0,
                "minValue": purchase_data['price'].min() if any(purchase_data['price']) else 0,
                "adsQty": len(purchase_data),
                "date": datetime.now().strftime('%Y-%m-%d')
            },
            "generalValue": {
                "avgValue": all_data['price'].mean() if any(all_data['price']) else 0,
                "maxValue": all_data['price'].max() if any(all_data['price']) else 0,
                "minValue": all_data['price'].min() if any(all_data['price']) else 0,
                "adsQty": len(all_data),
                "date": datetime.now().strftime('%Y-%m-%d')
            }
        }

    @staticmethod
    def _map_history_values(all_result):
        history_values = []
        for key, value in all_result.items():
            value['date'] = key.strftime('%Y-%m-%d')
            history_values.append(value)
        return history_values

    @staticmethod
    def get_history_values(start, end, freq):
        params = USDValueHelper.solr_base_params
        params['fq'] = 'external_created_at:[{}T00:00:00Z TO {}T23:59:59Z]'.format(start, end)

        # computing sale value history
        params['q'] = '\"' + '\" OR \"'.join(USDValueHelper.sale_phrase_queries) + '\"'
        sale_response = USDValueHelper.solr_request(params)
        sale_data = pd.read_csv(io.StringIO(sale_response.content.decode('utf-8')))
        sale_data = stats.exchange_rates_computation_service.standardize_prices(sale_data)
        sale_data = stats.exchange_rates_computation_service.remove_price_outliers(sale_data)
        sale_data['external_created_at'] = pd.to_datetime(sale_data['external_created_at'])
        # refer to https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases for freq
        # possible values
        sale_result = sale_data.groupby(pd.Grouper(key='external_created_at', freq=freq)).agg(
            avgValue=('price', 'mean'),
            maxValue=('price', 'max'),
            minValue=('price', 'min'),
            adsQty=('id', 'nunique')
        ).fillna(0).to_dict('index')
        # mapping Timestamp keys to str
        sale_result = USDValueHelper._map_history_values(sale_result)

        # computing purchase history value
        params['q'] = '\"' + '\" OR \"'.join(USDValueHelper.purchase_phrase_queries) + '\"'
        purchase_response = USDValueHelper.solr_request(params)
        purchase_data = pd.read_csv(io.StringIO(purchase_response.content.decode('utf-8')))
        purchase_data = stats.exchange_rates_computation_service.standardize_prices(purchase_data)
        purchase_data = stats.exchange_rates_computation_service.remove_price_outliers(purchase_data)
        purchase_data['external_created_at'] = pd.to_datetime(purchase_data['external_created_at'])
        purchase_result = purchase_data.groupby(pd.Grouper(key='external_created_at', freq=freq)).agg(
            avgValue=('price', 'mean'),
            maxValue=('price', 'max'),
            minValue=('price', 'min'),
            adsQty=('id', 'nunique')
        ).fillna(0).to_dict('index')
        purchase_result = USDValueHelper._map_history_values(purchase_result)

        # computing general value
        all_data = pd.concat([sale_data, purchase_data])
        all_result = all_data.groupby(pd.Grouper(key='external_created_at', freq=freq)).agg(
            avgValue=('price', 'mean'),
            maxValue=('price', 'max'),
            minValue=('price', 'min'),
            adsQty=('id', 'nunique')
        ).fillna(0).to_dict('index')
        all_result = USDValueHelper._map_history_values(all_result)

        return {
            'saleHistory': sale_result,
            'purchaseHistory': purchase_result,
            'generalHistory': all_result
        }

    @staticmethod
    def solr_request(params):
        query = USDValueHelper.solr_base_path + "/?{}".format(urlencode(params))
        return requests.get(query)

