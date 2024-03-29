# Generated by Django 3.0.7 on 2021-09-09 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0028_telegramgroup_link_and_username_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='ad',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Deleted at'),
        ),
        migrations.AlterField(
            model_name='ad',
            name='contact_tg',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Contact telegram'),
        ),
    ]
