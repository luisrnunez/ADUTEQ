# Generated by Django 4.2.3 on 2023-07-30 14:15

import Prestamos.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0002_remove_socios_activo_remove_socios_apellidos_and_more'),
        ('ayudas_econ', '0003_ayudaseconomicas_valorsocio'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetallesAyuda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=8)),
                ('evidencia', models.FileField(blank=True, null=True, upload_to=Prestamos.models.upload_to_evidencia)),
                ('cancelado', models.BooleanField(default=False)),
                ('ayuda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ayudas_econ.ayudaseconomicas')),
                ('socio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socios.socios')),
            ],
        ),
    ]
