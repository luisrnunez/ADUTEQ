# Generated by Django 4.2.2 on 2023-07-08 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pagos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagos',
            name='fecha_consumo',
            field=models.DateField(),
        ),
    ]
