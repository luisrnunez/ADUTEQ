# Generated by Django 4.2.4 on 2023-09-12 22:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayudas_econ', '0002_consumoscuotaordinaria_ayudaseconomicas_brinda_ayuda_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ayudaseconomicas',
            name='total',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True),
        ),
    ]