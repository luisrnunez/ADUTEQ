# Generated by Django 4.2.3 on 2023-07-10 01:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proveedor',
            name='RUC',
            field=models.CharField(max_length=13, unique=True),
        ),
    ]
