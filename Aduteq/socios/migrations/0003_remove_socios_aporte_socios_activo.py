# Generated by Django 4.2.2 on 2023-06-27 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0002_alter_socios_foto'),
    ]

    operations = [
        migrations.AddField(
            model_name='socios',
            name='activo',
            field=models.BooleanField(default=True),
        ),
    ]
