# Generated by Django 3.1 on 2021-09-29 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csgo', '0003_auto_20210929_1226'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={},
        ),
        migrations.RemoveField(
            model_name='inventoryitem',
            name='is_listed',
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='item_state',
            field=models.CharField(choices=[('INVENTORY', 'INVENTORY'), ('LISTED', 'LISTED'), ('TRANSACTION', 'TRANSACTION'), ('SOLD', 'SOLD')], default='INVENTORY', max_length=32),
        ),
    ]
