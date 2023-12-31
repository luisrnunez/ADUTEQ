# Generated by Django 4.2.3 on 2023-07-30 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0002_alter_proveedor_ruc'),
    ]

    operations = [
        migrations.AddField(
            model_name='proveedor',
            name='cupo',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=8),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='proveedor',
            name='comision',
            field=models.IntegerField(),
        ),
    ]
