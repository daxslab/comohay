# Generated by Django 3.0.7 on 2021-01-15 18:57

from django.db import migrations

from ads.models import User


def add_anonymous_user(apps, schema_editor):
    anon = User.objects.create_user(username='anonymous')
    anon.save()

class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0021_add_not_unique_ads_slug'),
    ]

    operations = [
        migrations.RunPython(add_anonymous_user),
    ]
