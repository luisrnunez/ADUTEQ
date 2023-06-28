# Generated by Django 4.2.2 on 2023-06-25 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='proveedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('telefono', models.IntegerField(max_length=13)),
                ('RUC', models.IntegerField(max_length=13)),
                ('direccion', models.CharField(max_length=500)),
                ('comision', models.FloatField()),
            ],
        ),
    ]
