# Generated by Django 3.1 on 2021-09-18 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgo', '0031_auto_20210918_1130'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryitem',
            name='is_listed',
            field=models.BooleanField(default=False),
        ),
    ]
