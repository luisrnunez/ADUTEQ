# Generated by Django 4.2.3 on 2023-09-15 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0007_total_ayuda_permanente_total_cuota_ordinaria'),
    ]

    operations = [
        migrations.AddField(
            model_name='total_cuota_ordinaria',
            name='tipo',
            field=models.CharField(default='s', max_length=1),
            preserve_default=False,
        ),
    ]
