# Generated by Django 3.0.7 on 2020-07-27 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0017_add_ad_external_contact_id_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='external_created_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='External created at'),
        ),
    ]
