# Generated by Django 4.2.3 on 2023-08-15 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Pagos', '0006_alter_detalle_cuotas_evidencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalle_cuotas',
            name='valor_cuota',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8),
            preserve_default=False,
        ),
    ]
