import json
from datetime import datetime

from categories.models import Category
from django.utils.timezone import make_aware

from ads.models import Province, Municipality, Ad
from scraper.items import AdItem
from scraper.spiders.base import BaseSpider


class HogarencubaSpider(BaseSpider):
  name = "hogarencuba"
  source = 'hogarencuba.com'
  start_urls = ["https://hogarencuba.com/api.json"]


  def parse(self, response):

      results = json.loads(response.body)

      for property in results:

          location = property['location']
          province_text = None
          municipality_text = None

          try:
              province_text = location.split(',')[-1].strip()
              municipality_text = location.split(',')[-2].strip()
          except:
              pass

          if municipality_text == 'Cumanayagüa':
              municipality_text = 'Cumanayagua'
          elif municipality_text == 'La Habana del Este':
              municipality_text = 'Habana del Este'

          if province_text == 'Sancti Spiritus':
              province_text = 'Sancti Spíritus'

          province = Province.objects.get(name=province_text) if province_text else None
          municipality = Municipality.objects.get(name=municipality_text,
                                                  province=province.id) if municipality_text and province_text else None

          category = Category.objects.filter(name='Compra y venta de viviendas', parent__name='Inmuebles').get()

          item = AdItem()
          item['title'] = property['title']
          item['category'] = category
          item['description'] = property['description']
          item['price'] = property['price']
          item['currency_iso'] = Ad.AMERICAN_DOLLAR_ISO
          item['province'] = province
          item['municipality'] = municipality
          item['external_source'] = self.source
          item['external_id'] = property['id']
          item['external_url'] = property['url']
          item['external_created_at'] = make_aware(datetime.fromtimestamp(property['created_at']))

          yield item
