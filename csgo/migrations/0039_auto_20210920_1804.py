# Generated by Django 3.1 on 2021-09-20 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgo', '0038_auto_20210920_1759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='tournament',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
