from concurrent.futures.thread import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from categories.models import Category

from ads.importers.base import BaseImporter
from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province


CATEGORY_MAPPING = {
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

def get_category_tree(bc_category):
    for category in CATEGORY_MAPPING:
        for bc_category_name in CATEGORY_MAPPING[category]:
            if bc_category == bc_category_name:
                return (category, CATEGORY_MAPPING[category][bc_category_name],)

    return ('Misceláneas', 'Otros',)


class BachecubanoImporter(BaseImporter):

    product_pages = [
        'https://www.bachecubano.com/computadoras',
        'https://www.bachecubano.com/electronica',
        'https://www.bachecubano.com/servicios',
        'https://www.bachecubano.com/hogar',
        'https://www.bachecubano.com/transporte',
        'https://www.bachecubano.com/salud-y-belleza',
        'https://www.bachecubano.com/otros',
    ]

    source = 'bachecubano.com'

    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'

    custom_headers = {'User-Agent': user_agent}

    def run(self):
        self.remove_normalized_data_duplicates()
        self.import_data()
        # self.remove_old_data()

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

    def get_item(self, item):
        product_link = item.select('.product-title > a')[0]['href']
        try:
            item_response = requests.get(product_link, headers=self.custom_headers)
            item_soup = BeautifulSoup(item_response.content, 'html.parser')

            title = item_soup.select('h1.product-title')[0].text

            category = None
            province = None
            _advertisement = item_soup.select('ul.advertisement > li')
            for a in _advertisement:
                e = a.select('strong')[0]
                if e.text == 'Categoría:':
                    bc_category = a.select('a')[0].text
                    category_tree = get_category_tree(bc_category)
                    category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).get()
                elif e.text == ' Ubicación:':
                    bc_province = a.select('a')[0].text
                    province = Province.objects.get(name=bc_province) if bc_province else None

            description = item_soup.select('#content')[0].get_text()

            _price_element = item_soup.select('.description-info .short-info .ads-btn h3')[0]
            if _price_element and _price_element.text:
                price = _price_element.text.split(' ')[1]
            else:
                price = 0

            external_source = self.source
            external_id = product_link.split('/')[-1]
            external_url = product_link
            print(external_id, external_source)

            self.normalized_data.append(dict(
                title=title,
                category=category,
                description=description,
                price=float(price),
                user_currency='CUC',
                province=province,
                # municipality=municipality,
                external_source=external_source,
                external_id=external_id,
                external_url=external_url
            ))
        except Exception as e:
            self.logger.error('could not load product "%s". %s', product_link, e)

    def get_normalized_data(self):
        self.normalized_data = []
        for page in self.product_pages:
            try:
                response = requests.get(page, headers=self.custom_headers)
                items_list_soup = BeautifulSoup(response.content, 'html.parser')
                elements = items_list_soup.select('.product-item')

                with ThreadPoolExecutor(max_workers=self.workers) as executor:
                    for item in elements:
                        executor.submit(self.get_item, item)

            except Exception as e:
                self.logger.error('could not load products page "%s". %s', page, e)


        return self.normalized_data

