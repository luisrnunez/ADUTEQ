# Generated by Django 4.2.2 on 2023-06-27 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socios',
            name='foto',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]