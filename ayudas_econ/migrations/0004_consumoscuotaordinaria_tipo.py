# Generated by Django 4.2.3 on 2023-09-15 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayudas_econ', '0003_alter_ayudaseconomicas_total'),
    ]

    operations = [
        migrations.AddField(
            model_name='consumoscuotaordinaria',
            name='tipo',
            field=models.CharField(default='r', max_length=1),
            preserve_default=False,
        ),
    ]
