from categories.models import Category
from html2text import HTML2Text

from ads.models import Province, Municipality
from scraper.items import AdItem
from scraper.spiders.base import BaseSpider


class RevolicoSpider(BaseSpider):
    name = "revolico"
    source = 'revolico.com'
    category_mapping = {
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
    start_urls = [
        'https://www.revolico.com/compra-venta/',
        'https://www.revolico.com/empleos/',
        'https://www.revolico.com/autos/',
        'https://www.revolico.com/servicios/',
        'https://www.revolico.com/vivienda/',
        'https://www.revolico.com/computadoras/',
    ]

    def parse(self, response):
        ad_page_links = response.css('.container-fluid ul li[data-cy=adRow] a[href]')
        yield from response.follow_all(ad_page_links, self.parse_ad)

        next_page = response.css('#paginator-next::attr(href)').get()
        if next_page is not None and self.depth > 0:
            self.depth -= 1
            yield response.follow(next_page, callback=self.parse)

    def parse_ad(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        title = extract_with_css('h4[data-cy=adTitle]::text')

        rv_category = response.css('main .container-fluid ol[data-cy=breadcrumb] span > li > a > span::text').getall()[1].strip()
        category_tree = self.get_category_tree(rv_category)
        category = Category.objects.filter(name=category_tree[1], parent__name=category_tree[0]).get()

        rv_location = response.css('main .container-fluid > div:first-of-type > div:first-of-type > div:nth-of-type(2) > div:nth-of-type(2) div::text').get().strip()
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

        html_handler = HTML2Text()
        description = html_handler.handle(response.css('div[data-cy=adDescription]').get())

        e = extract_with_css('main .container-fluid > div:first-of-type > div:first-of-type > div:nth-of-type(1) h4:nth-of-type(2)::text')
        if len(e) > 1:
            e_parts = e.split(' ')
            price = e_parts[0]
            currency = e_parts[1] if e_parts[1] in ['CUC', 'CUP'] else 'CUC'
        else:
            price = 0
            currency = 'CUC'

        phone = None
        _phone_url = extract_with_css('a[data-cy="adPhone"]::attr(href)')
        if _phone_url:
            phone = self.clean_phone(_phone_url.split(':')[1])

        email = None
        _email_url = extract_with_css('a[data-cy="adEmail"]::attr(href)')
        if _email_url:
            email = _email_url.split(':')[1]

        external_id = extract_with_css('div[data-cy=adId]::text')
        external_url = response.request.url

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

        yield item