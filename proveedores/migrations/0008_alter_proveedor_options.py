# Generated by Django 4.2.3 on 2023-09-11 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0007_rename_ruc_proveedor_ruc'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proveedor',
            options={'ordering': ['nombre']},
        ),
    ]