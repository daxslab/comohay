# Generated by Django 3.0.7 on 2020-07-22 20:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0016_auto_20200716_0255'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='external_contact_id',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='External contact ID'),
        ),
    ]