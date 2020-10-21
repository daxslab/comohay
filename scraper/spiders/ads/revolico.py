from datetime import datetime

from categories.models import Category
from django.utils.timezone import make_aware

from ads.models import Province, Municipality
from scraper.items import AdItem
from scraper.spiders.ads.base import BaseParser


class RevolicoParser(BaseParser):

    category_mapping = {
        'Computadoras': {
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
            'Implementos Deportivos': 'Artículos deportivos',
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

    def parse_ad(self, ad):
        title = ad['node']['title']

        rv_category = ad['node']['subcategory']['title']
        category_tree = self.get_category_tree(rv_category)
        category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).get()

        rv_municipality = ad['node']['municipality']['name'] if ad['node']['municipality'] else None
        rv_province = ad['node']['province']['name'] if ad['node']['province'] else None
        province = Province.objects.get(name=rv_province) if rv_province else None
        try:
            municipality = Municipality.objects.get(name=rv_municipality) if rv_municipality else None
        except:
            municipality = None

        description = ad['node']['description']

        price = ad['node']['price']
        currency = ad['node']['currency'] if ad['node']['currency'] in ['CUC', 'CUP'] else 'CUC'

        phone = self.clean_phone(ad['node']['phone']) if ad['node']['phone'] else None
        # email = ad['node']['email']
        email = None

        external_date = ad['node']['updatedOnByUser']
        external_created_at = datetime.strptime(external_date.split('+')[0].split('.')[0], "%Y-%m-%dT%H:%M:%S")
        external_created_at = make_aware(external_created_at)

        external_id = ad['node']['id']
        external_url = 'https://www.revolico.com'+ad['node']['permalink']

        item = AdItem()
        item['title'] = title
        item['category'] = category
        item['description'] = description
        item['price'] = price
        item['user_currency'] = currency
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

    def is_not_found(self, response):
        if response.css('h2::text').get(default='').strip() in ['Anuncio eliminado.', 'Anuncio inválido.', 'Anuncio despublicado.']:
            return True
        return False
