from datetime import datetime

from categories.models import Category
from django.utils.timezone import make_aware
from html2text import HTML2Text

from ads.models import Province, Municipality
from scraper.items import AdItem
from scraper.spiders.ads.base import BaseParser


class MerolicoParser(BaseParser):

    category_mapping = {
        'Computadoras':{
            'Pc de Escritorio': 'PC',
            'Monitores': 'Monitores',
            'Motherboard': 'Accesorios y Componentes',
            'Chasis/Fuentes': 'Accesorios y Componentes',
            'Tarjeta Video/Sonido': 'Accesorios y Componentes',
            'Disco Duro': 'Accesorios y Componentes',
            'Teclado/Mouse': 'Accesorios y Componentes',
            'Memoria Ram': 'Accesorios y Componentes',
            'Memorias Flash': 'Accesorios y Componentes',
            'Impresora/Cartuchos': 'Impresoras',
            'Bocinas/Audífonos': 'Accesorios y Componentes',
            'Modem/Wifi/Internet': 'Modem y Red',
            'Software y Juegos': 'Otros Computadoras',
            'Otros componentes': 'Otros Computadoras',
            'Reproductor Mp3/Mp4': 'Audio',
            'Cámara/Foto/Video': 'Cámara Foto/Video',
            'Móviles en venta': 'Celulares y Accesorios',
            'Accesorios Móviles': 'Celulares y Accesorios',
            'Piezas de Móviles': 'Celulares y Accesorios',
            'Talleres Móviles': 'Centros de reparaciones',
            'Laptops': 'Laptop',
            'Componentes de Laptops': 'Accesorios y Componentes',
            'Tablets/IPad': 'Tablets',
            'Consolas en venta': 'Consolas y Videojuegos',
            'Accesorios': 'Consolas y Videojuegos',
            'Video Juegos': 'Consolas y Videojuegos',
            'Reparación': 'Consolas y Videojuegos',
        },
        'Electrodomésticos': {
            'Reproductor DVD/VCD': 'Reproductores de video',
            'Televisores en venta': 'TV',
            'Aires Acondicionados': 'Aire Acondicionado',
            'Electrodomésticos': 'Otros Electrodomésticos',
        },
        'Misceláneas': {
            'Muebles y Decoración': 'Muebles y Decoración',
            'Ropas y Zapatos': 'Ropas, Zapatos y Accesorios',
            'Mascotas y Accesorios': 'Animales y Mascotas',
            'Libros y Revistas': 'Otros',
            'Prendas y Relojes': 'Otros',
            'Antigüedades y Colección': 'Otros',
            'Implementos deportivos': 'Artículos deportivos',
            'Ferretería/Construcción': 'Otros',
            'Útiles del Hogar': 'Artículos para el hogar',
            'Otros artículos': 'Otros',
            'Juguetes y regalos': 'Artículos para niños',
            'Lactancia y alimentación': 'Artículos para niños',
        },
        'Servicios': {
            'Clases/Cursos': 'Cursos',
            'Construcción/Mantenimiento': 'Otros Servicios',
            'Diseño/Decoración': 'Diseño y Decoración',
            'Informática/Programación': 'Informática',
            'Traductor/Escritor': 'Traducción y Edición',
            'Gimnasio/Masajista': 'Salud y Belleza',
            'Técnico/Reparaciones': 'Otros Servicios',
            'Videos/Fotografía': 'Fotografía y Video',
            'Marketing/Publicidad': 'Otros Servicios',
            'Otros servicios': 'Otros Servicios',
        },
        'Inmuebles': {
            'Casas en venta': 'Compra y venta de viviendas',
            'Permutas': 'Permutas',
            'Alquiler por mes/año': 'Alquiler',
            'Renta por horas/días': 'Arrendamiento',
            'Terrenos/Garajes': 'Otros Inmuebles',
            'Agentes Inmobiliarios': 'Otros Inmuebles',
        },
        'Transporte': {
            'Carros en venta': 'Autos',
            'Motos en venta': 'Motos',
            'Bicicletas en venta': 'Bicicletas',
            'Taller de Reparación': 'Taller',
            'Piezas y Accesorios': 'Partes y Piezas',
        },
        'Empleo': {
            'Ofertas de trabajo': 'Ofrezco',
            'Busco empleo': 'Necesito',
        },
    }


    def parse_ad(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        title = extract_with_css('h1::text')

        category_text = response.css('.ads-details-wrapper span.category::text').extract()[1].rstrip().strip()
        category_tree = self.get_category_tree(category_text)
        category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).first()

        province = None
        province_text = response.css('.ads-details-wrapper span.item-location::text').extract()
        if len(province_text) > 1:
            province_text = province_text[1].rstrip().strip()
        else:
            province_text = None
        if province_text:
            province = Province.objects.get(name=province_text.split(',')[0].strip())
        municipality = None
        if province_text:
            _split_text = province_text.split(',')
            if len(_split_text) > 1:
                municipality_text = _split_text[1].strip()
                try:
                    municipality = Municipality.objects.get(name=municipality_text) if municipality_text else None
                except Exception as e:
                    self.logger.error('Error including municipality "%s": %s' % (municipality_text, str(e)))

        html_handler = HTML2Text()
        description = html_handler.handle(response.css('div.Ads-Details div.ads-details-info').get())

        price = 0
        price_text = response.css('h1 span::text').extract()
        if len(price_text) > 1:
            price = price_text[1].rstrip().strip()
        if price:
            price = price.replace(',', '')
        else:
            price = 0
        currency_text = extract_with_css('h1 span small:nth-of-type(2)::text')

        if currency_text and 'usd' in currency_text.lower():
            currency = 'CUC'
        elif currency_text and 'cuc' in currency_text.lower():
            currency = 'CUC'
        elif currency_text and 'cup' in currency_text.lower():
            currency = 'CUP'
        else:
            currency = 'CUC'

        contact_phone= None
        contact_phone_info = response.css('.card-user-info .ev-action a.btn-info::text').extract()
        if len(contact_phone_info) > 1:
            contact_phone = self.clean_phone(contact_phone_info[1].rstrip().strip())

        external_date_string = extract_with_css('span.date span::attr(date-time)')
        external_created_at = datetime.strptime(external_date_string, "%Y-%m-%d %H:%M:%S")
        external_created_at = make_aware(external_created_at)

        external_id = response.request.url
        external_url = response.request.url

        item = AdItem()
        item['title'] = title
        item['category'] = category
        item['description'] = description
        item['price'] = price
        item['user_currency'] = currency
        item['province'] = province
        item['municipality'] = municipality
        item['contact_phone'] = contact_phone
        item['contact_email'] = None
        item['external_source'] = self.source
        item['external_id'] = external_id
        item['external_url'] = external_url
        item['external_contact_id'] = None
        item['external_created_at'] = external_created_at

        return item
