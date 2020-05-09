import requests
from bs4 import BeautifulSoup
from categories.models import Category

from ads.importers.base import BaseImporter
from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province


CATEGORY_MAPPING = {
    'Computadoras':{
        'Celulares/Líneas/Accesorios': 'Celulares y Accesorios',
        'Reproductor MP3/MP4/IPOD': 'Audio',
        'Cámara Foto/Video': 'Cámara Foto/Video',
        'Consola Videojuego/Juegos': 'Consolas y Videojuegos',
        'PC de Escritorio': 'PC',
        'Laptop': 'Laptop',
        'Microprocesador': 'Accesorios y Componentes',
        'Monitor': 'Monitores',
        'Motherboard': 'Accesorios y Componentes',
        'Memoria RAM/FLASH': 'Accesorios y Componentes',
        'Disco Duro Interno/Externo': 'Accesorios y Componentes',
        'Chasis/Fuente': 'Accesorios y Componentes',
        'Tarjeta de Video': 'Accesorios y Componentes',
        'Tarjeta de Sonido/Bocinas': 'Accesorios y Componentes',
        'Quemador/Lector DVD/CD': 'Accesorios y Componentes',
        'Backup/UPS': 'Accesorios y Componentes',
        'Impresora/Cartuchos': 'Impresoras',
        'Modem/Wifi/Red': 'Modem y Red',
        'Webcam/Microf/Audífono': 'Accesorios y Componentes',
        'Teclado/Mouse': 'Accesorios y Componentes',
        'Internet/Email': 'Modem y Red',
        'CD/DVD Virgen': 'CD, DVD y Blu-ray',
        'Otros': 'Otros Computadoras',
    },
    'Electrodomésticos': {
        'Televisor': 'TV',
        'Aire Acondicionado': 'Aire Acondicionado',
        'Satélite': 'Otros Electrodomésticos',
        'Electrodomésticos': 'Otros Electrodomésticos',
        'Reproductor DVD/VCD/DVR': 'Reproductores de video',

    },
    'Misceláneas': {
        'Muebles/Decoración': 'Muebles y Decoración',
        'Ropa/Zapato/Accesorios': 'Ropas, Zapatos y Accesorios',
        'Intercambio/Regalo': 'Otros',
        'Mascotas/Animales': 'Animales y Mascotas',
        'Implementos Deportivos':'Artículos deportivos',
        'Arte': 'Arte',
    },
    'Servicios': {
        'Divisas': 'Cambio de Moneda',
        'Clases/Cursos': 'Cursos',
        'Informática/Programación': 'Informática',
        'Películas/Series/Videos': 'Entretenimiento',
        'Limpieza/Doméstico': 'Domésticos',
        'Foto/Video': 'Fotografía y Video',
        'Construcción/Mantenimiento': 'Albañilería',
        'Reparación Electrónica': 'Reparación electrónica',
        'Peluquería/Barbería/Belleza': 'Peluquerías y Barberías',
        'Restaurantes/Gastronomía': 'Gastronomía',
        'Diseño/Decoración': 'Diseño y Decoración',
        'Música/Animación/Shows': 'Entretenimiento',
        'Relojero/Joyero': 'Relojerías y Joyeros',
        'Gimnasio/Masaje/Entrenador': 'Gimnasios y Masajistas',
        'Otros': 'Otros Servicios',
    },
    'Inmuebles': {
        'Compra/Venta': 'Compra y venta de viviendas',
        'Permuta': 'Permutas',
        'Alquiler a cubanos': 'Alquiler',
        'Alquiler a extranjeros': 'Arrendamiento',
        'Casa en la playa': 'Arrendamiento',
    },
    'Empleo': {
        'Ofertas de empleo': 'Ofrezco',
        'Busco empleo': 'Necesito',
    },
    'Transporte': {
        'Carros': 'Autos',
        'Motos': 'Motos',
        'Bicicletas': 'Bicicletas',
        'Piezas/Accesorios': 'Partes y Piezas',
        'Alquiler': 'Otros Transporte',
        'Mecánico': 'Taller',
        'Otros': 'Otros Transporte',
    },
}

def get_category_tree(bc_category):
    for category in CATEGORY_MAPPING:
        for bc_category_name in CATEGORY_MAPPING[category]:
            if bc_category == bc_category_name:
                return (category, CATEGORY_MAPPING[category][bc_category_name],)

    return ('Misceláneas', 'Otros',)


class RevolicoImporter(BaseImporter):

    base_url = 'https://www.revolico.com'

    product_pages = [
        'https://www.revolico.com/compra-venta/',
        'https://www.revolico.com/empleos/',
        'https://www.revolico.com/autos/',
        'https://www.revolico.com/servicios/',
        'https://www.revolico.com/vivienda/',
        'https://www.revolico.com/computadoras/',
    ]

    source = 'revolico.com'

    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'

    custom_headers = {'User-Agent': user_agent}

    def run(self):
        self.remove_normalized_data_duplicates()
        self.import_data()
        # self.remove_old_data()
        pass

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
        for page in self.product_pages:
            try:
                response = requests.get(page, headers=self.custom_headers)
                items_list_soup = BeautifulSoup(response.content, 'html.parser')
                elements = items_list_soup.select('.container-fluid ul li[data-cy=adRow]')

                for item in elements:
                    anchors = item.select('a')
                    product_link = None
                    for anchor in anchors:
                        if anchor.has_attr('href'):
                            product_link = anchor['href']
                    try:
                        item_response = requests.get(self.base_url+product_link, headers=self.custom_headers)
                        item_soup = BeautifulSoup(item_response.content, 'html.parser')

                        title = item_soup.select('h4[data-cy=adTitle]')[0].find(text=True, recursive=False)

                        rv_category = item_soup.select('main .container-fluid ol[data-cy=breadcrumb] span > li > a > span')[1].getText()
                        category_tree = get_category_tree(rv_category)
                        category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).get()

                        rv_first_data_div = item_soup.select('main .container-fluid > div:first-of-type > div:first-of-type')
                        rv_location_div = rv_first_data_div[0].select('div')[1]
                        rv_location = rv_location_div.select('div')[2].getText()
                        location_elements = rv_location.split(',')

                        rv_municipality = None
                        if len(location_elements) > 1:
                            rv_municipality = location_elements[0].strip()
                            rv_province = location_elements[1].strip()
                        else:
                            rv_province = location_elements[0].strip()
                        province = Province.objects.get(name=rv_province) if rv_province else None
                        try:
                            municipality = Municipality.objects.get(name=rv_municipality) if rv_municipality else None
                        except:
                            municipality = None

                        description = item_soup.select('div[data-cy=adDescription]')[0].get_text()


                        _price_title_container = rv_first_data_div[0].select('div')[0]
                        e = _price_title_container.select('h4')
                        if len(e) > 1:
                            price = e[1].getText().split(' ')[0]
                        else:
                            price = 0

                        external_source = self.source
                        external_id = item_soup.select('div[data-cy=adId]')[0].get_text()
                        external_url = self.base_url+product_link
                        print(external_id, external_source)

                        self.normalized_data.append(dict(
                            title=title,
                            category=category,
                            description=description,
                            price=price,
                            province=province,
                            municipality=municipality,
                            external_source=external_source,
                            external_id=external_id,
                            external_url=external_url
                        ))
                    except Exception as e:
                        self.logger.error('could not load product "%s". %s', product_link, e)
            except Exception as e:
                self.logger.error('could not load products page "%s". %s', page, e)


        return self.normalized_data

