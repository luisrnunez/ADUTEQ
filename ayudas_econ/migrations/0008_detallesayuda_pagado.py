# Generated by Django 4.2.3 on 2023-09-05 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayudas_econ', '0007_alter_detallesayuda_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='detallesayuda',
            name='pagado',
            field=models.BooleanField(default=False),
        ),
    ]
