import json

from categories.models import Category

from ads.models import Province, Municipality
from scraper.items import AdItem
from scraper.spiders.base import BaseSpider


class HogarencubaSpider(BaseSpider):
  name = "hogarencuba"
  source = 'hogarencuba.com'
  start_urls = ["https://hogarencuba.com/api.json"]


  def parse(self, response):
      # data = response.css("div.st-about-employee-pop-up")

      results = json.loads(response.body)

      for property in results:

          location = property['location']
          province_text = None
          municipality_text = None

          try:
              province_text = location.split('/')[0]
              municipality_text = location.split('/')[1]
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
          item['user_currency'] = 'CUC'
          item['province'] = province
          item['municipality'] = municipality
          item['external_source'] = self.source
          item['external_id'] = property['id']
          item['external_url'] = property['url']

          yield item
