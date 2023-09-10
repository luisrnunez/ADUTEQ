# Generated by Django 4.2.3 on 2023-09-09 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0005_alter_socios_fecha_nacimiento_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Total_Ayuda_Permanente',
            fields=[
                ('tipo_aportacion', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('total_actual', models.DecimalField(decimal_places=2, max_digits=8)),
                ('fecha_transaccion', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Total_Cuota_Ordinaria',
            fields=[
                ('tipo_aportacion', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('total_actual', models.DecimalField(decimal_places=2, max_digits=8)),
                ('fecha_transaccion', models.DateField()),
            ],
        ),
    ]
