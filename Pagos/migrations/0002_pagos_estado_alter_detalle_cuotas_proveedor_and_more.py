# Generated by Django 4.2.3 on 2023-08-28 02:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proveedores', '0006_detallescupos_permanente'),
        ('socios', '0004_alter_aportaciones_socio'),
        ('Pagos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagos',
            name='estado',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='detalle_cuotas',
            name='proveedor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='proveedores.proveedor'),
        ),
        migrations.AlterField(
            model_name='detalle_cuotas',
            name='socio',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='socios.socios'),
        ),
        migrations.AlterField(
            model_name='detalle_cuotas',
            name='valor_cuota',
            field=models.DecimalField(decimal_places=2, default=120, max_digits=8),
        ),
    ]
