# Generated by Django 4.2.3 on 2023-07-30 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socios', '0003_aportaciones'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aportaciones',
            name='socio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socios.socios'),
        ),
    ]
