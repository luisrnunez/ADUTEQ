# Generated by Django 4.2.3 on 2023-09-02 13:04

from django.db import migrations, models
import promociones.models


class Migration(migrations.Migration):

    dependencies = [
        ('promociones', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocion',
            name='evidencia',
            field=models.FileField(blank=True, null=True, upload_to=promociones.models.upload_to_evidencia),
        ),
        migrations.AlterField(
            model_name='promocion',
            name='fecha_fin',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='promocion',
            name='fecha_inicio',
            field=models.DateField(),
        ),
    ]
