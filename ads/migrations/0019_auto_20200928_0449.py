# Generated by Django 3.0.7 on 2020-09-28 04:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0018_add_ad_external_created_at_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ad',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Contact phone'),
        ),
    ]
