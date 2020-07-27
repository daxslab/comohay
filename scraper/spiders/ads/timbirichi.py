from datetime import datetime, timedelta

from categories.models import Category
from django.utils.timezone import make_aware
from html2text import HTML2Text

from ads.models import Province, Municipality
from scraper.items import AdItem
from scraper.spiders.ads.base import BaseParser


class TimbirichiParser(BaseParser):
    category_mapping = {
        'Computadoras': {
            'PC Completa/Kits': 'PC',
            'Laptop': 'Laptop',
            'Laptop Accesorios': 'Accesorios y Componentes',
            'Monitores': 'Monitores',
            'Motherboard': 'Accesorios y Componentes',
            'Tarjeta de Video': 'Accesorios y Componentes',
            'Disco Duro': 'Accesorios y Componentes',
            'Fuentes/Chasis': 'Accesorios y Componentes',
            'Microprocesador': 'Accesorios y Componentes',
            'Tarjeta de Sonido': 'Accesorios y Componentes',
            'Lector/Quemador': 'Accesorios y Componentes',
            'Backup': 'Accesorios y Componentes',
            'Teclado y Mouse': 'Accesorios y Componentes',
            'Memoria Ram': 'Accesorios y Componentes',
            'Tarjeta de Red': 'Accesorios y Componentes',
            'Hubs/Regletas': 'Accesorios y Componentes',
            'Cables/Adaptadores': 'Accesorios y Componentes',
            'Impresora/Cartuchos': 'Impresoras',
            'Modem/Wifi/Internet': 'Modem y Red',
            'Bocinas': 'Audio',
            'CD/DVD': 'CD, DVD y Blu-ray',
            'Audífonos/Micróf/Wcam': 'Otros Computadoras',
            'Consolas/Videojuegos': 'Consolas y Videojuegos',
            'Móviles': 'Celulares y Accesorios',
            'Tabletas': 'Tablets',
            'Cables/Cargadores': 'Celulares y Accesorios',
            'Forros/Micas': 'Celulares y Accesorios',
            'Baterías': 'Celulares y Accesorios',
            'Piezas': 'Celulares y Accesorios',
            'Batería Externa': 'Celulares y Accesorios',
            'Aplicaciones': 'Otros Computadoras',
            'Servicios a Móviles': 'Centros de reparaciones',
        },
        'Electrodomésticos': {
            'Televisores': 'TV',
            'Refrigerador/Nevera': 'Refrigeradores',
            'Aire Acondicionado/Split': 'Aire Acondicionado',
            'Ventiladores': 'Otros Electrodomésticos',
            'Cocinas/Hornos': 'Cocinas',
            'Lavadoras': 'Lavadoras',
            'Batidora/Licuadora': 'Otros Electrodomésticos',
            'Teléfonos': 'Otros Electrodomésticos',
            'Cajita Digital': 'Otros Electrodomésticos',
            'Antena Interior/Exterior': 'Otros Electrodomésticos',
            'Baterías/Cargador': 'Otros Electrodomésticos',
            'Flash/MicroSD/Memorias': 'Otros Electrodomésticos',
        },
        'Misceláneas': {
            'Reproductor Portatíl': 'Útiles y herramientas',
            'Antiguedad y Colección': 'Otros',
            'Aseo/Perfumería': 'Perfumería y Cosméticos',
            'Cámara/Foto/Video': 'Audio y Video Multimedia',
            'Implementos Deportivos': 'Artículos deportivos',
            'Ferretería/Construcción': 'Otros',
            'Instrumentos Musicales': 'Instrumentos musicales',
            'Mascotas/Accesorios': 'Animales y Mascotas',
            'Luces/Iluminación': 'Otros',
            'Útiles del Hogar': 'Artículos para el hogar',
            'Electrónica/Herramientas': 'Útiles y herramientas',
            'Regalos/Juguetes': 'Otros',
            'Alimentos/Bebidas': 'Otros',
            'Útiles de Belleza': 'Perfumería y Cosméticos',
            'Muebles': 'Muebles y Decoración',
            'Decoración': 'Muebles y Decoración',
            'Otros': 'Otros',
            'Programas/Contenido Digital': 'Audio y Video Multimedia',
            'Libros/Revistas': 'Otros',
            'Ropa Prendas Accesorios': 'Ropas, Zapatos y Accesorios',
        },
        'Servicios': {
            'Recarga/Transferencia': 'Otros Servicios',
            'Talleres de Reparación': 'Reparación electrónica',
            'Presentaciones/Eventos': 'Organización de eventos',
            'Construcción/Mantenimiento': 'Otros Servicios',
            'Fiesta/Show/Animación': 'Organización de eventos',
            'Carpintería/Cristalería': 'Otros Servicios',
            'Contenido Digital/Programas': 'Otros Servicios',
            'Decoración/Diseño': 'Diseño y Decoración',
            'Electrónico': 'Reparación electrónica',
            'Agencia Publicitaria': 'Otros Servicios',
            'Peluquería/Barbería/Belleza': 'Peluquerías y Barberías',
            'Masajista': 'Otros Servicios',
            'Refrigeración/Clima': 'Otros Servicios',
            'Programador/Informático': 'Informática',
            'Profesor/Clases': 'Cursos',
            'Excursiones/Viajes': 'Viajes y Turismo',
            'Traductor/Interprete': 'Traducción y Edición',
            'Tramites/Gestiones': 'Otros Servicios',
            'Joyería': 'Otros Servicios',
            'Otros Servicios': 'Otros Servicios',
        },
        'Inmuebles': {
            'Casa/Apartamento': 'Compra y venta de viviendas',
            'Permuta': 'Permutas',
            'Renta a Extranjeros': 'Arrendamiento',
            'Renta a Cubanos': 'Arrendamiento',
            'Locales/Espacios': 'Otros Inmuebles',
            'Casa en la Playa': 'Otros Inmuebles',
            'Gestor Inmobiliario': 'Otros Inmuebles',
        },
        'Transporte': {
            'Carros': 'Autos',
            'Motos': 'Motos',
            'Bicicletas': 'Bicicletas',
            'Transporte y Taxis': 'Otros Transporte',
            'Patinetas/Carriolas': 'Otros Transporte',
            'Útiles/Accesorios': 'Partes y Piezas',
            'Piezas de Carros': 'Partes y Piezas',
            'Piezas de Moto': 'Partes y Piezas',
            'Piezas de Bicicleta': 'Partes y Piezas',
            'Luces/Bombillos': 'Partes y Piezas',
            'Taller/Mecánico': 'Taller',
            'Otros Medios': 'Otros Transporte',
            'Camiones/Camionetas': 'Camiones',
        },
        'Empleo': {
            'Ofrezco Empleo': 'Ofrezco',
            'Busco Empleo': 'Necesito',
        },
    }

    def parse_ad(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        title = extract_with_css('h4.title-item-gris::text')

        category_text = extract_with_css('ul.breadcrumb > li:nth-of-type(3) > a::text')
        category_tree = self.get_category_tree(category_text)
        category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).first()
        province_text = extract_with_css('ul.publicado-por div.avatar > p:last-of-type::text')
        province = Province.objects.get(name=province_text) if province_text else None

        html_handler = HTML2Text()
        description = html_handler.handle(response.css('div.panel-body > div:first-of-type').get())

        _price_element = extract_with_css('h4.title-item-gris precio::text')
        if _price_element:
            price = _price_element.split(' ')[1].replace(',', '')
        else:
            price = 0

        phone = None
        _phone_url = extract_with_css('ul.publicado-por li.button-anounces a.btn-success::attr(href)')
        if _phone_url:
            phone = self.clean_phone(_phone_url.split(':')[1])

        external_date_text = extract_with_css('fecha::text')
        external_created_at = None
        if 'segundo' in external_date_text:
            external_created_at = datetime.now() - timedelta(seconds=int(external_date_text.split(' ')[1]))
        elif 'minuto' in external_date_text:
            external_created_at = datetime.now() - timedelta(minutes=int(external_date_text.split(' ')[1]))
        elif 'hora' in external_date_text:
            external_created_at = datetime.now() - timedelta(hours=int(external_date_text.split(' ')[1]))
        elif 'día' in external_date_text or 'dia' in external_date_text:
            external_created_at = datetime.now() - timedelta(days=int(external_date_text.split(' ')[1]))
        elif 'semana' in external_date_text:
            external_created_at = datetime.now() - timedelta(days=7 * int(external_date_text.split(' ')[1]))
        elif 'mes' in external_date_text:
            external_created_at = datetime.now() - timedelta(days=30 * int(external_date_text.split(' ')[1]))
        elif 'año' in external_date_text:
            external_created_at = datetime.now() - timedelta(days=365 * int(external_date_text.split(' ')[1]))

        if external_created_at:
            external_created_at = make_aware(external_created_at)

        external_id = response.request.url.split('-')[-1]
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
        item['contact_email'] = None
        item['external_source'] = self.source
        item['external_id'] = external_id
        item['external_url'] = external_url
        item['external_contact_id'] = None
        item['external_created_at'] = external_created_at

        return item
