# Generated by Django 4.2.3 on 2023-09-10 20:32

import Prestamos.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0007_alter_socios_options'),
        ('ayudas_econ', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsumosCuotaOrdinaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.TextField(max_length=300)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=8)),
                ('fecha', models.DateField()),
                ('evidencia', models.FileField(blank=True, null=True, upload_to=Prestamos.models.upload_to_evidencia)),
            ],
        ),
        migrations.AddField(
            model_name='ayudaseconomicas',
            name='valorsocio',
            field=models.DecimalField(decimal_places=2, default='0', max_digits=8),
        ),
        migrations.AlterField(
            model_name='ayudaseconomicas',
            name='fecha',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='ayudaseconomicas',
            name='socio',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='socios.socios'),
        ),
        migrations.CreateModel(
            name='DetallesAyuda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=8)),
                ('evidencia', models.FileField(blank=True, null=True, upload_to=Prestamos.models.upload_to_evidencia)),
                ('fecha', models.DateField(null=True)),
                ('cancelado', models.BooleanField(default=False)),
                ('pagado', models.BooleanField(default=False)),
                ('ayuda', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ayudas_econ.ayudaseconomicas')),
                ('socio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socios.socios')),
            ],
        ),
        migrations.CreateModel(
            name='AyudasExternas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.TextField(max_length=200)),
                ('cedula', models.TextField(max_length=10)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=8)),
                ('fecha', models.DateField()),
                ('detalle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ayudas_econ.ayudaseconomicas')),
            ],
        ),
    ]
