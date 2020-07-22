from categories.models import Category
from html2text import HTML2Text

from ads.models import Province, Municipality
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

        _price_element = extract_with_css('div.l-right div.v-price b::text')
        if _price_element and 'usd' in _price_element.lower():
            price = ''.join(_price_element.split(' ')[:-1]).replace(" ", "")
            currency = 'CUC'
        elif _price_element and 'cuc' in _price_element.lower():
            price = ''.join(_price_element.split(' ')[:-1]).replace(" ", "")
            currency = 'CUC'
        elif _price_element and 'cup' in _price_element.lower():
            price = ''.join(_price_element.split(' ')[:-1]).replace(" ", "")
            currency = 'CUP'
        else:
            price = 0
            currency = 'CUC'

        external_contact_id = extract_with_css('div.v-author__info > span > a::attr(href)')
        if external_contact_id:
            external_contact_id = external_contact_id.strip('/').split('/')[-1]

        external_id = extract_with_css('#sid::text')[1:]
        external_url = response.request.url

        item = AdItem()
        item['title'] = title
        item['category'] = category
        item['description'] = description
        item['price'] = price
        item['user_currency'] = currency
        item['province'] = province
        # item['municipality'] = municipality
        item['contact_phone'] = None
        item['contact_email'] = None
        item['external_source'] = self.source
        item['external_id'] = external_id
        item['external_url'] = external_url
        item['external_contact_id'] = external_contact_id

        return item
