# Generated by Django 3.0.7 on 2020-07-12 16:12
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0012_search'),
    ]

    operations = [
        TrigramExtension(),
    ]