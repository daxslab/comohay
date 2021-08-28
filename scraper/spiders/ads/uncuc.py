import re
from datetime import datetime

from categories.models import Category
from django.utils.timezone import make_aware
from html2text import HTML2Text

from ads.models import Province, Municipality, Ad
from scraper.items import AdItem
from scraper.spiders.ads.base import BaseParser


class UncucParser(BaseParser):

    category_mapping = {
        'Computadoras':{
            'Teléfonos Móviles - Accesorios': 'Celulares y Accesorios',
        },
        'Electrodomésticos': {
            'Electrónica / Equipos de Cocina': 'Otros Electrodomésticos',
        },
        'Misceláneas': {
            'Ropa / Zapatos / Otros': 'Otros',
            'Belleza / Salud / Cosmético': 'Otros',
            'Mascotas / Animales': 'Animales y Mascotas',
            'Deportes / Ocio': 'Otros',
            'Productos para Bebés / Niños': 'Otros',
            'Afición / Música / Arte': 'Otros',
            'Alimentos / Bebidas / Otros': 'Otros',
            'Sin Fines de Lucro': 'Otros',
        },
        'Servicios': {
            'Mueblería / Jardinería / Otros - Belleza': 'Otros Servicios',
            'Servicios': 'Otros Servicios',
            'Construcción / Reparación': 'Otros Servicios',
            'Cursos / Educación': 'Cursos',
        },
        'Inmuebles': {
            'Bienes Raíces / Casas': 'Otros Inmuebles',
        },
        'Transporte': {
            'Transporte': 'Otros Transporte',
        },
        'Empleo': {
            'Trabajo / Empleo': 'Ofrezco',
        },
    }

    months = {
        'enero': '01',
        'febrero': '02',
        'marzo': '03',
        'abril': '04',
        'mayo': '05',
        'junio': '06',
        'julio': '07',
        'agosto': '08',
        'septiembre': '09',
        'octubre': '10',
        'noviembre': '11',
        'diciembre': '12',
    }


    def parse_ad(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        title = extract_with_css('h1.v-title b::text')

        category_text = extract_with_css('ul.breadcrumb > li:nth-of-type(2) > a::text')
        category_tree = self.get_category_tree(category_text)
        category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).first()
        province_text = extract_with_css('div.l-main__content div.hidden-phone span.v-map-point::text')
        province_text = ' '.join(province_text.split(' ')[:-1]).strip()
        province = Province.objects.filter(name=province_text).first()

        html_handler = HTML2Text()
        description = html_handler.handle(response.css('div.v-descr_text').get())

        price = 0
        currency = Ad.CUBAN_PESO_ISO

        _price_element = extract_with_css('div.l-right div.v-price b::text')
        _price_element = _price_element.replace(" ", "")

        if _price_element:

            match = re.search('(?P<price>\d+(\.\d+)?)(?P<curr>.+)?', _price_element)

            if match:
                price = match.group('price') if match.group('price') else price
                currency_str = match.group('curr')

                if currency_str:
                    if currency_str == '$':
                        currency = Ad.AMERICAN_DOLLAR_ISO
                    else:
                        for currency_iso_tuple in Ad.ALLOWED_CURRENCIES:
                            if currency_iso_tuple[0].lower() == currency_str.lower():
                                currency = currency_iso_tuple[0]
                                break

        external_contact_id = extract_with_css('div.v-author__info > span > a::attr(href)')
        if external_contact_id:
            external_contact_id = external_contact_id.strip('/').split('/')[-1]

        # external_date_string = extract_with_css('div.l-main__content div.hidden-phone div.v-info small::text')
        # external_date_string = response.css('div.l-main__content div.hidden-phone div.v-info small').extract()
        external_created_at = None
        _info = response.css('div.l-main__content div.hidden-phone div.v-info small::text').extract()
        for text in _info:
            if 'Insertado' in text:
                external_date_string = text.split(':')[1].strip()
                pattern = re.compile("|".join(self.months.keys()))
                processed_date_string = pattern.sub(lambda m: self.months[re.escape(m.group(0))], external_date_string)
                external_created_at = datetime.strptime(processed_date_string, "%d %m %Y")

        if external_created_at:
            external_created_at = make_aware(external_created_at)

        external_id = extract_with_css('#sid::text')[1:]
        external_url = response.request.url

        item = AdItem()
        item['title'] = title
        item['category'] = category
        item['description'] = description
        item['price'] = price
        item['currency_iso'] = currency
        item['province'] = province
        # item['municipality'] = municipality
        item['contact_phone'] = None
        item['contact_email'] = None
        item['external_source'] = self.source
        item['external_id'] = external_id
        item['external_url'] = external_url
        item['external_contact_id'] = external_contact_id
        item['external_created_at'] = external_created_at

        return item
