# Generated by Django 3.1 on 2021-09-12 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_auto_20210908_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.URLField(default='ad.com'),
            preserve_default=False,
        ),
    ]