# Generated by Django 3.1 on 2021-09-21 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='classid',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='listing',
            name='instanceid',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
