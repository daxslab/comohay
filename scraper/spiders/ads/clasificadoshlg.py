from categories.models import Category
from html2text import HTML2Text

from ads.models import Province, Municipality
from scraper.items import AdItem
from scraper.spiders.ads.base import BaseParser


class ClasificadoshlgParser(BaseParser):

    category_mapping = {
        'Computadoras':{
            'Teléfonos Móviles - Accesorios': 'Celulares y Accesorios',
            'Computadoras ,part , acce...': 'PC',
            'Equipos de Red, redes, etc': 'Modem y Red',
            'Videojuegos - Consolas': 'Consolas y Videojuegos',
        },
        'Electrodomésticos': {
            'Equipos electricos y electrónicos': 'Otros Electrodomésticos',
        },
        'Misceláneas': {
            'Ropa y Peleteria': 'Ropas, Zapatos y Accesorios',
            'Para Niños y Bebés': 'Artículos para niños',
            'Joyas - Relojes': 'Otros',
            'Arte - Piezas de coleccionista': 'Otros',
            'Hogar - Jardín - Muebles': 'Otros',
            'Instrumentos Musicales': 'Instrumentos musicales',
            'Juguetes - Juegos - Aficiones': 'Otros',
            'Animales': 'Animales y Mascotas',
            'Libros, Revistas y Cómics': 'Otros',
            'Artículos de deporte - Bicicletas': 'Artículos deportivos',
        },
        'Servicios': {
            'Salud - Belleza': 'Salud y Belleza',
            'Informática - Diseño web': 'Cursos',
            'Clases de Música - Teatro - Da': 'Cursos',
            'Tutores - Clases Particulares': 'Cursos',
            'Otros Cursos': 'Cursos',
            'Canguros - Niñeras': 'Cuidados a domicilio',
            'Casting - Audiciones': 'Otros Servicios',
            'Ordenadores': 'Informática',
            'Servicios de Eventos': 'Organización de eventos',
            'Salud - Belleza - Fitness': 'Salud y Belleza',
            'Horóscopo - Tarot': 'Otros Servicios',
            'Servicio - Ayuda Doméstica': 'Domésticos',
            'Mudanza - Almacenaje': 'Otros Servicios',
            'Reparaciones': 'Otros Servicios',
            'Redacción - Edición - Traducción': 'Traducción y Edición',
            'Otros Servicios': 'Traducción y Edición',
            'Compartir coche': 'Otros Servicios',
        },
        'Inmuebles': {
            'Venta de Garaje': 'Garajes y Estacionamientos',
            'Entradas': 'Otros Inmuebles',
            'Alquiler de Habitaciones': 'Alquiler',
            'Locales en Alquiler - En Venta ': 'Otros Inmuebles',
        },
        'Transporte': {
            'Coches': 'Autos',
            'Piezas de Coches': 'Partes y Piezas',
            'Motorinas , part y acce...': 'Motos',
            'Motocicletas , part. acce...': 'Motos',
            'Caravanas - Autocaravanas': 'Otros Transporte',
            'Camiones - Vehículos Comerciales': 'Camiones',
            'Otros Vehículos': 'Otros Transporte',
        },
        'Empleo': {
            'Contabilidad - Finanzas': 'Ofrezco',
            'Publicidad - Relaciones Públicas': 'Ofrezco',
            'Arte - Entretenimiento - Literatura': 'Ofrezco',
            'Administrativo': 'Ofrezco',
            'Servicio al Cliente': 'Ofrezco',
            'Educación - Entrenamiento': 'Ofrezco',
            'Ingenieros - Arquitectos': 'Ofrezco',
            'Salud': 'Ofrezco',
            'Recursos Humanos': 'Ofrezco',
            'Internet': 'Ofrezco',
            'Legal': 'Ofrezco',
            'Trabajo Manual': 'Ofrezco',
            'Producción - Operaciones': 'Ofrezco',
            'Marketing': 'Ofrezco',
            'Sin ánimo de lucro - Voluntarios': 'Ofrezco',
            'Inmobiliaria': 'Ofrezco',
            'Restaurantes - Comida': 'Ofrezco',
            'Ventas al detalle': 'Ofrezco',
            'Ventas': 'Ofrezco',
            'Tecnología': 'Ofrezco',
            'Otros Empleos': 'Ofrezco',
        },
    }


    def parse_ad(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        title = extract_with_css('h1 strong::text')

        category_text = extract_with_css('ul.breadcrumb > li:nth-of-type(2) > a > span::text')
        category_tree = self.get_category_tree(category_text)
        category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).first()
        province = Province.objects.get(name='Holguín')

        html_handler = HTML2Text()
        description = html_handler.handle(response.css('div.description p:first-of-type').get())

        _price_element = extract_with_css('h1 span::text')
        if _price_element and 'Dollar US$' in _price_element:
            price = _price_element.split(' ')[0]
            currency = 'CUC'
        elif _price_element and 'CUC' in _price_element:
            price = _price_element.split(' ')[0]
            currency = 'CUC'
        elif _price_element and 'CUP' in _price_element:
            price = _price_element.split(' ')[0]
            currency = 'CUP'
        else:
            price = 0
            currency = 'CUC'

        external_id = response.request.url
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
        item['external_contact_id'] = None

        return item
