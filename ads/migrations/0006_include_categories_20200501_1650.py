# Generated by Django 3.0.5 on 2020-05-01 16:50
from categories.models import Category
from django.db import migrations

categories = {
    'Computadoras': [
        'PC',
        'Laptop',
        'Monitores',
        'Tablets',
        'Celulares y Accesorios',
        'Impresoras',
        'Fotocopiadoras',
        'Modem y Red',
        'CD, DVD y Blu-ray',
        'Audio',
        'Consolas y Videojuegos',
        'Accesorios y Componentes',
        'Centros de reparaciones',
        'Cámara Foto/Video',
        'Otros Computadoras',
    ],
    'Electrodomésticos': [
        'TV',
        'Reproductores de video',
        'Lavadoras',
        'Refrigeradores',
        'Planchas',
        'Cocinas',
        'Microwaves',
        'Cafeteras eléctricas',
        'Taller de Reparaciones',
        'Aire Acondicionado',
        'Otros Electrodomésticos',
    ],
    'Misceláneas': [
        'Arte',
        'Artículos para niños',
        'Artículos deportivos',
        'Artículos para el hogar',
        'Animales y Mascotas',
        'Joyas',
        'Instrumentos musicales',
        'Perfumería y Cosméticos',
        'Ropas, Zapatos y Accesorios',
        'Muebles y Decoración',
        'Audio y Video Multimedia',
        'Útiles y herramientas',
        'Otros',
    ],
    'Inmuebles': [
        'Alquiler',
        'Arrendamiento',
        'Compra y venta de viviendas',
        'Construcción y Mantenimiento',
        'Garajes y Estacionamientos',
        'Terrenos y Parcelas',
        'Permutas',
        'Otros Inmuebles',
    ],
    'Empleo': [
        'Ofrezco',
        'Necesito',
    ],
    'Transporte': [
        'Autos',
        'Camiones',
        'Jeep',
        'Motos',
        'Embarcaciones',
        'Bicicletas',
        'Partes y Piezas',
        'Taller',
        'Otros Transporte',
    ],
    'Servicios': [
        'Cuidados a domicilio',
        'Domésticos',
        'Gastronomía',
        'Jardinería',
        'Organización de eventos',
        'Salud y Belleza',
        'Cursos',
        'Traducción y Edición',
        'Repasadores',
        'Taxis',
        'Viajes y Turismo',
        'Mudanza',
        'Albañilería',
        'Diseño y Decoración',
        'Reparación electrónica',
        'Entretenimiento',
        'Fotografía y Video',
        'Informática',
        'Peluquerías y Barberías',
        'Relojerías y Joyeros',
        'Gimnasios y Masajistas',
        'Cambio de Moneda',
        'Otros Servicios',
    ]
}

def add_categories(apps, schema_editor):
    for main_category in categories:
        mc = Category(name=main_category)
        mc.save()
        for subcategory in categories[main_category]:
            sc = Category(parent=mc, name=subcategory)
            sc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0005_rename_ads_url_field_20200426_2053'),
    ]

    operations = [
        migrations.RunPython(add_categories),
    ]
