from categories.models import Category
from django.core.management.base import BaseCommand, CommandError
from django_seed import Seed

from ads.models import User
from ads.models.ad import Ad
from ads.models.municipality import Municipality
from ads.models.province import Province


class Command(BaseCommand):
    help = 'Creates dummy data for testing proposes'

    def handle(self, *args, **options):
        seeder = Seed.seeder('es_ES')
        # seeder.add_entity(Category, 7, {
        #     'parent': lambda x: None,
        #     'thumbnail': lambda x: '',
        #     'thumbnail_width': lambda x: None,
        #     'thumbnail_height': lambda x: None,
        #     'order': lambda x: 0,
        #     'alternate_url': lambda x: '',
        #     'description': lambda x: '',
        #     'meta_keywords': lambda x: '',
        #     'meta_extra': lambda x: '',
        # })
        # seeder.add_entity(Province, 7)
        # seeder.add_entity(Municipality, 5)
        tmp_province = Province.objects.order_by('?')[0]
        seeder.add_entity(Ad, 500, {
            'category': lambda x: Category.objects.exclude(parent=None).order_by('?')[0],
            'province': lambda x: tmp_province,
            'municipality': lambda x: Municipality.objects.order_by('?')[0],
            'created_by': User.objects.all()[0],
            'updated_by': User.objects.all()[0]
        })
        seeder.execute()
        # incude valid provinces
        for ad in Ad.objects.all():
            ad.province = ad.municipality.province
            ad.save()