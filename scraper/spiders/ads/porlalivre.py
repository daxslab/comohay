import re
from datetime import datetime, timedelta

from categories.models import Category
from django.utils.timezone import make_aware
from html2text import HTML2Text
from scrapy import Selector

from ads.models import Province, Municipality
from scraper.items import AdItem
from scraper.spiders.ads.base import BaseParser

PROVINCE_MAPPING = {
    'habana': 'La Habana',
    'matanzas': 'Matanzas',
    'cienfuegos': 'Cienfuegos',
    'sanctispiritus': 'Sancti Spíritus',
    'tunas': 'Las Tunas',
    'holguin': 'Holguín',
    'granma': 'Granma',
    'santiago': 'Santiago de Cuba',
    'isla': 'Isla de la Juventud',
    'camaguey': 'Camagüey',
    'ciego': 'Ciego de Ávila',
    'villaclara': 'Villa Clara',
    'guantanamo': 'Guantánamo',
    'pinar': 'Pinar del Río',
    'artemisa': 'Artemisa',
    'mayabeque': 'Mayabeque'
}

class PorlalivreParser(BaseParser):

    category_mapping = {
        'Computadoras': {
            'Celulares en venta': 'Celulares y Accesorios',
            'Piezas / Accesorios': 'Accesorios y Componentes',
            'Software / Reparación': 'Centros de reparaciones',
            'Se compra celulares': 'Otros Computadoras',
            'Laptops en venta': 'Laptop',
            'Componentes de Laptop': 'Accesorios y Componentes',
            'Tablets / Ipad': 'Tablets',
            'Se compra portátil': 'Otros Computadoras',
            'Cámaras Foto / Video': 'Cámara Foto/Video',
            'Computadoras en venta': 'PC',
            'Componentes de PC': 'Accesorios y Componentes',
            'Almacenamiento Externo': 'Accesorios y Componentes',
            'Memorias USB / Tarjetas': 'Accesorios y Componentes',
            'Impresoras / Insumos': 'Impresoras',
            'Protección / Backup': 'Accesorios y Componentes',
            'Redes / Modems': 'Modem y Red',
            'CD / DVD / Blu-ray': 'CD, DVD y Blu-ray',
            'Software / Juegos': 'Otros Computadoras',
            'Consolas en venta': 'Consolas y Videojuegos',
            'Accesorios p/Consolas': 'Accesorios y Componentes',
            'Juegos / Reparación': 'Otros Computadoras',
            'Se compra consola': 'Consolas y Videojuegos',
        },
        'Electrodomésticos': {
            'TV / Audio / Video': 'Electrodomésticos',
            'Electrodomésticos': 'Electrodomésticos',
        },
        'Misceláneas': {
            'Antigüedades / Colecciones': 'Otros',
            'Aseo / Perfumería': 'Perfumería y Cosméticos',
            'Deportes / Fitness': 'Otros',
            'Instrumentos musicales': 'Instrumentos musicales',
            'Libros / Revistas': 'Otros',
            'Mascotas / Accesorios': 'Animales y Mascotas',
            'Muebles / Decoración': 'Muebles y Decoración',
            'Para bebés / niños': 'Artículos para niños',
            'Ropa / Calzados': 'Ropas, Zapatos y Accesorios',
            'Salud / Hogar': 'Otros',
            'Cualquier otra cosa': 'Otros',
        },
        'Servicios': {
            'Agentes Inmobiliarios': 'Otros Servicios',
            'Ferretería / Construcción': 'Servicios',
            'Películas / Música': 'Entretenimiento',
            'Relojes / Joyas': 'Relojerías y Joyeros',
            'Belleza / Estilo': 'Salud y Belleza',
            'Clases / Cursos': 'Cursos',
            'Construcción / Mantenimiento': 'Otros Servicios',
            'Diseño / Impresiones': 'Otros Servicios',
            'Escritura / Traducción': 'Traducción y Edición',
            'Gimnasio / Masajista': 'Gimnasios y Masajistas',
            'Guarderías / Doméstico': 'Domésticos',
            'Informática / Programación': 'Informática',
            'Paladares / Cafeterías': 'Gastronomía',
            'Para bodas / quinces': 'Organización de eventos',
            'Técnico / Reparaciones': 'Reparación electrónica',
            'Trámites / Promociones': 'Otros Servicios',
            'Video / Fotografía': 'Fotografía y Video',
            'Otros servicios': 'Otros Servicios',
        },
        'Inmuebles': {
            'Casas en venta': 'Compra y venta de viviendas',
            'Se Permuta': 'Permutas',
            'Alquiler por mes/año': 'Alquiler',
            'Renta por horas/días': 'Arrendamiento',
            'Terrenos / Garajes': 'Otros Inmuebles',
        },
        'Empleo': {
            'Ofertas de trabajo': 'Ofrezco',
            'Se busca empleo': 'Necesito',
        },
        'Transporte': {
            'Carros en venta': 'Autos',
            'Motos / Scooters': 'Motos',
            'Partes / Piezas': 'Partes y Piezas',
            'Taxi / Rentas': 'Otros Transporte',
            'Taller / Reparaciones': 'Taller',
            'Bicicletas / Accesorios': 'Bicicletas',
        },
    }

    months = {
        'enero': '01',
        'febrero':'02',
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

        'ene.': '01',
        'feb.': '02',
        'mar.': '03',
        'abr.': '04',
        'may.': '05',
        'jun.': '06',
        'jul.': '07',
        'ago.': '08',
        'sept.': '09',
        'oct.': '10',
        'nov.': '11',
        'dic.': '12',
    }

    def _get_province(self, url):
        page = url.split('/')[2]
        page_parts = page.split('.')
        if page_parts == 3:
            for province_slug in PROVINCE_MAPPING:
                if province_slug == page_parts[0]:
                    return PROVINCE_MAPPING[province_slug]
            raise Exception('Unknown province {province}'.format(province=page_parts[0]))
        else:
            return 'La Habana'

    def get_category_tree(self, bc_category):
        for category in self.category_mapping:
            for bc_category_name in self.category_mapping[category]:
                if bc_category == bc_category_name and category == self.category_mapping[category][bc_category_name]:
                    return (category, )
                elif bc_category == bc_category_name:
                    return (category, self.category_mapping[category][bc_category_name],)

        return ('Misceláneas', 'Otros',)

    def parse_ad(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        raw_title = extract_with_css('h1::text')
        if raw_title.endswith('-'):
            title = raw_title.replace('\n', '')[:-1]
        else:
            title = raw_title

        # pl_category_container = item_soup.select('div#classified-header ul li')[3]
        # pl_category = pl_category_container.find(text=True, recursive=False)
        pl_category = extract_with_css('div#classified-header ul li:nth-of-type(4)::text')
        category_tree = self.get_category_tree(str(pl_category.strip()))
        if len(category_tree) == 1:
            category = Category.objects.filter(name=category_tree[0], parent=None).get()
        else:
            category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).get()

        # pl_location_container = item_soup.select('div#classified-header ul li')[2]
        # pl_location = pl_location_container.find(text=True, recursive=False)
        pl_location = extract_with_css('div#classified-header ul li:nth-of-type(3)::text')
        pl_municipality = None
        if re.findall('\(([^)]+)', pl_location):
            pl_municipality = re.findall('\(([^)]+)', pl_location)[0]
        pl_province = self._get_province(response.request.url)
        try:
            municipality = Municipality.objects.get(name=pl_municipality) if pl_municipality else None
        except:
            municipality = None
        province = Province.objects.get(name=pl_province) if pl_province else None

        # description = item_soup.select('div.classified-content > div.panel')[0].get_text()
        html_handler = HTML2Text()
        description = html_handler.handle(response.css('div.classified-content > div.panel').get())

        price = 0
        # a = item_soup.select('h1 span')
        # if item_soup.select('h1 span'):
        #     price = item_soup.select('h1 span')[0].getText().strip().replace(',', '')[1:]
        raw_price = extract_with_css('h1 span::text')
        if raw_price:
            price = raw_price.replace(',', '')[1:]

        phone = None
        contacts_elements = response.css('div.contact-info li').getall()
        for element in contacts_elements:
            if str(element).find('fa-phone') != -1:
                raw_phone = Selector(text=str(element)).css('li::text').get()
                if raw_phone:
                    phone = self.clean_phone(raw_phone)

        email = None
        _email_url = extract_with_css('div.contact-info a[href^="mailto:"]::attr(href)')
        if _email_url:
            email = _email_url.split(':')[1]

        if 'ad_date' in response.meta:
            if 'hoy' in response.meta['ad_date']:
                external_created_at = datetime.now()
            elif 'ayer' in response.meta['ad_date']:
                external_created_at = datetime.now() - timedelta(days=1)
            else:
                external_date_string = response.meta['ad_date']
                for name, value in self.months.items():
                    external_date_string = external_date_string.replace(name, value)
                external_created_at = datetime.strptime(external_date_string, "%m %d, %Y")

            external_created_at = make_aware(external_created_at)
        else:
            external_created_at = None

        # external_id = item_soup.select('div#classified-header ul li')[0].find(text=True, recursive=False).strip()
        external_id = extract_with_css('div#classified-header ul li::text')
        external_url = response.request.url

        item = AdItem()
        item['title'] = title
        item['category'] = category
        item['description'] = description
        item['price'] = price
        item['user_currency'] = 'CUC'
        item['province'] = province
        item['municipality'] = municipality
        item['contact_phone'] = phone
        item['contact_email'] = email
        item['external_source'] = self.source
        item['external_id'] = external_id
        item['external_url'] = external_url
        item['external_contact_id'] = None
        item['external_created_at'] = external_created_at

        return item