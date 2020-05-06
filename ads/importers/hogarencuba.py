import json
from urllib import request

from categories.models import Category

from ads.importers.base import BaseImporter
from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province


class HogarencubaImporter(BaseImporter):

    api_url = 'http://localhost/hogarencuba-less.json'

    source = 'hogarencuba.com'

    def run(self):
        self.import_data()
        self.remove_old_data()

    def import_data(self):
        for ad_data in self.normalized_data:
            try:
                Ad.objects.update_or_create(
                    external_source = self.source,
                    external_id = ad_data['external_id'],
                    defaults = ad_data
                )
            except Exception as e:
                self.logger.error('Could not save normalized data. {exception} {data}'.format(exception=str(e), data=str(ad_data)))

    def remove_old_data(self):
        external_ids = [data['external_id'] for data in self.normalized_data]
        Ad.objects.filter(external_source=self.source).exclude(external_id__in=external_ids).delete()

    def get_normalized_data(self):
        self.normalized_data = []
        with request.urlopen(self.api_url) as response:
            data = json.load(response)
            for property in data:
                try:
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

                    self.normalized_data.append(dict(
                                title=property['title'],
                                category=category,
                                description=property['description'],
                                price=property['price'],
                                province=province,
                                municipality=municipality,
                                external_source=self.source,
                                external_id=property['id'],
                                external_url=property['url']
                            ))
                except Exception as e:
                    self.logger.error('Could not obtain normalized data. {exception} {data}'.format(exception=str(e), data=str(property)))
