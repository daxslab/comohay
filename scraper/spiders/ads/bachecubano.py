from categories.models import Category
from html2text import HTML2Text
from scrapy import Selector

from ads.models import Province, Municipality
from scraper.items import AdItem
from scraper.spiders.ads.base import BaseParser


class BachecubanoParser(BaseParser):

    category_mapping = {
        'Computadoras':{
            'Disco duros': 'Accesorios y Componentes',
            'Pc de Escritorio': 'PC',
            'Microprocesadores': 'Accesorios y Componentes',
            'Memorias': 'Accesorios y Componentes',
            'Redes y WiFi': 'Modem y Red',
            'Chasis y Fuentes': 'Accesorios y Componentes',
            'Motherboards': 'Accesorios y Componentes',
            'Tarjetas de video': 'Accesorios y Componentes',
            'Monitores': 'Monitores',
            'Impresoras y Cartuchos': 'Impresoras',
            'Teclados y Mouse': 'Accesorios y Componentes',
            'Portátiles y Tablets' : 'Laptop',
            'Unidad de CD y DVD' : 'Accesorios y Componentes',
            'Audio y Bocinas' : 'Accesorios y Componentes',
            'Backups' : 'Accesorios y Componentes',
            'Celulares': 'Celulares y Accesorios',
            'Consolas de Videojuegos': 'Consolas y Videojuegos',
        },
        'Electrodomésticos': {
            'Televisores': 'TV',
            'Aire Acondicionado': 'Aire Acondicionado',
            'Electrodomésticos': 'Otros Electrodomésticos',
        },
        'Misceláneas': {
            'Cámaras fotográficas': 'Útiles y herramientas',
            'Audio y Video Multimedia': 'Audio y Video Multimedia',
            'Mascotas': 'Animales y Mascotas',
            'Muebles y Decoración': 'Muebles y Decoración',
            'Obras de Arte': 'Arte',
            'Implementos deportivos': 'Artículos deportivos',
            'Vestuario y Calzado': 'Ropas, Zapatos y Accesorios',
        },
        'Servicios': {
            'Albañilería': 'Albañilería',
            'Clases': 'Cursos',
            'Diseño y Decoración': 'Diseño y Decoración',
            'Reparación electrónica': 'Reparación electrónica',
            'Entretenimiento': 'Entretenimiento',
            'Espectáculos': 'Organización de eventos',
            'Fotografía y Video': 'Fotografía y Video',
            'Gastronomía': 'Gastronomía',
            'Idiomas': 'Cursos',
            'Informática': 'Informática',
            'Otros Servicios': 'Otros Servicios',
            'Peluquerías y Barberías': 'Peluquerías y Barberías',
            'Relojerías y Joyeros': 'Relojerías y Joyeros',
            'Servicios domésticos': 'Domésticos',
            'Bisutería y Relojes': 'Relojerías y Joyeros',
            'Gimnasios y Masajistas': 'Gimnasios y Masajistas',
            'Cambio de Moneda': 'Cambio de Moneda',
        },
        'Inmuebles': {
            'Alquiler de Casas': 'Alquiler',
            'Compra/Venta de Casas': 'Compra y venta de viviendas',
            'Permuta': 'Permutas',
        },
        'Transporte': {
            'Compra/Venta de Autos': 'Autos',
            'Bicicletas': 'Bicicletas',
            'Alquiler de Autos': 'Autos',
            'Talleres': 'Taller',
            'Motos': 'Motos',
            'Accesorios y Piezas': 'Partes y Piezas',
        },
        'Empleo': {
            'Empleos': 'Ofrezco',
        },
    }


    def parse_ad(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        title = extract_with_css('h1::text')

        category = None
        province = None
        # _advertisement = item_soup.select('ul.advertisement > li')
        _advertisement = response.css('ul.advertisement > li').getall()
        for a in _advertisement:
            e = Selector(text=a).css('strong::text').get()
            # e = a.select('strong')[0]
            if e == 'Categoría:':
                # bc_category = a.select('a')[0].text
                bc_category = Selector(text=a).css('a::text').get().strip()
                category_tree = self.get_category_tree(bc_category)
                category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).get()
            elif e == ' Ubicación:':
                # bc_province = a.select('a')[0].text
                bc_province = Selector(text=a).css('a::text').get().strip()
                province = Province.objects.get(name=bc_province) if bc_province else None

        html_handler = HTML2Text()
        description = html_handler.handle(response.css('#content').get())

        # _price_element = item_soup.select('.description-info .short-info .ads-btn h3')[0]
        _price_element = extract_with_css('.description-info .short-info .ads-btn h3::text')
        if _price_element:
            price = _price_element.split(' ')[1]
        else:
            price = 0

        phone = None
        _phone_url = extract_with_css('div.description-info .ads-btn > a[href^="tel:"]::attr(href)')
        if _phone_url:
            phone = _phone_url.split(':')[1]

        external_id = response.request.url.split('/')[-1]
        external_url = response.request.url

        item = AdItem()
        item['title'] = title
        item['category'] = category
        item['description'] = description
        item['price'] = price
        item['user_currency'] = 'CUC'
        item['province'] = province
        # item['municipality'] = municipality
        item['contact_phone'] = phone
        item['contact_email'] = ''
        item['external_source'] = self.source
        item['external_id'] = external_id
        item['external_url'] = external_url

        return item
