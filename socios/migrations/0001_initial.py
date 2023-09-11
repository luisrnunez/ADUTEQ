# Generated by Django 4.2.2 on 2023-07-05 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Socios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(default='user', max_length=50)),
                ('password', models.CharField(default='123', max_length=20, unique=True)),
                ('cedula', models.CharField(default='1250259114', max_length=10, unique=True)),
                ('nombres', models.CharField(default='Jose', max_length=100)),
                ('apellidos', models.CharField(default='Nuñez', max_length=100)),
                ('fecha_nacimiento', models.DateField(default='13/03/2001')),
                ('lugar_nacimiento', models.CharField(default='Quito', max_length=100)),
                ('correo_electronico', models.EmailField(default='user@gmail.com', max_length=254, unique=True)),
                ('numero_telefonico', models.CharField(default='0960138819', max_length=20, unique=True)),
                ('numero_convencional', models.CharField(default='0960138819', max_length=20)),
                ('direccion_domiciliaria', models.CharField(default='SANTO', max_length=100)),
                ('facultad', models.CharField(default='FCI', max_length=100)),
                ('categoria', models.CharField(default='Titular', max_length=100)),
                ('dedicacion_academica', models.CharField(default='INGENIERIA', max_length=100)),
                ('fecha_ingreso', models.DateField(default='2012')),
                ('titulo', models.CharField(default='INGENIERO ELECTRICO', max_length=100)),
                ('foto', models.BinaryField(blank=True, null=True)),
                ('aporte', models.CharField(default='13', max_length=5)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
    ]
