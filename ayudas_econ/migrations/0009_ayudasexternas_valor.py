# Generated by Django 4.2.4 on 2023-09-08 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ayudas_econ', '0008_ayudasexternas'),
    ]

    operations = [
        migrations.AddField(
            model_name='ayudasexternas',
            name='valor',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8),
            preserve_default=False,
        ),
    ]
