# Generated by Django 4.2.3 on 2023-08-15 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayudas_econ', '0005_detallesayuda_fecha'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ayudaseconomicas',
            name='fecha',
            field=models.DateField(),
        ),
    ]