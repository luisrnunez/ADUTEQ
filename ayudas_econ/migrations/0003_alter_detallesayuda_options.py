# Generated by Django 4.2.3 on 2024-03-09 05:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ayudas_econ', '0002_consumoscuotaordinaria_ayudaseconomicas_brinda_ayuda_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='detallesayuda',
            options={'ordering': ['socio__user__last_name']},
        ),
    ]
