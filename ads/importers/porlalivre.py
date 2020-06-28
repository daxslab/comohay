import re
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from categories.models import Category

from ads.importers.base import BaseImporter
from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province


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

# def get_category_tree(bc_category):
#     for category in CATEGORY_MAPPING:
#         for bc_category_name in CATEGORY_MAPPING[category]:
#             if bc_category == bc_category_name:
#                 return (category, CATEGORY_MAPPING[category][bc_category_name],)
#
#     return ('Misceláneas', 'Otros',)


class PorlalivreImporter(BaseImporter):

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

    base_url = 'https://porlalivre.com'

    base_pages = [
        '/viviendas/',
        # '/celulares/',
        # '/autos/',
        # '/portatiles/',
        # '/comunidad/',
        # '/se-vende/',
        # '/computadoras/',
        # '/consolas-juegos/',
        # '/servicios/',
    ]

    source = 'porlalivre.com'

    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'

    custom_headers = {'User-Agent': user_agent}

    def __init__(self):
        self.product_pages = []
        for base_page in self.base_pages:
            for province in PROVINCE_MAPPING:
                self.product_pages.append(self.base_url[:8] + province + '.' + self.base_url[8:] + base_page)
        super().__init__()

    def run(self):
        self.remove_normalized_data_duplicates()
        self.import_data()
        # self.remove_old_data()
        pass

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

    def get_item(self, item, page):
        product_link = item.select('a.classified-link')[0]['href']
        try:
            item_response = requests.get(self.base_url + product_link, headers=self.custom_headers)
            item_soup = BeautifulSoup(item_response.content, 'html.parser')

            title = item_soup.select('h1')[0].find(text=True, recursive=False)[:-2].replace("\n", "")

            pl_category_container = item_soup.select('div#classified-header ul li')[3]
            pl_category = pl_category_container.find(text=True, recursive=False)
            category_tree = self.get_category_tree(str(pl_category.strip()))
            if len(category_tree) == 1:
                category = Category.objects.filter(name=category_tree[0], parent=None).get()
            else:
                category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).get()

            pl_location_container = item_soup.select('div#classified-header ul li')[2]
            pl_location = pl_location_container.find(text=True, recursive=False)
            pl_municipality = None
            if re.findall('\(([^)]+)', pl_location):
                pl_municipality = re.findall('\(([^)]+)', pl_location)[0]
            pl_province = self._get_province(page)
            try:
                municipality = Municipality.objects.get(name=pl_municipality) if pl_municipality else None
            except:
                municipality = None
            province = Province.objects.get(name=pl_province) if pl_province else None

            description = item_soup.select('div.classified-content > div.panel')[0].get_text()

            price = 0
            a = item_soup.select('h1 span')
            if item_soup.select('h1 span'):
                price = item_soup.select('h1 span')[0].getText().strip().replace(',', '')[1:]

            external_source = self.source
            external_id = item_soup.select('div#classified-header ul li')[0].find(text=True, recursive=False).strip()
            external_url = self.base_url + product_link
            print(external_id, external_source)

            self.normalized_data.append(dict(
                title=title,
                category=category,
                description=description,
                price=float(price),
                user_currency='CUC',
                province=province,
                municipality=municipality,
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
                elements = items_list_soup.select('div.classified-wrapper')

                with ThreadPoolExecutor(max_workers=self.workers) as executor:
                    for item in elements:
                        executor.submit(self.get_item, item, page)

            except Exception as e:
                self.logger.error('could not load products page "%s". %s', page, e)


        return self.normalized_data

