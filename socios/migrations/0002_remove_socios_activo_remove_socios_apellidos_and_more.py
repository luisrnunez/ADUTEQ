# Generated by Django 4.2.2 on 2023-07-09 00:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('socios', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='socios',
            name='activo',
        ),
        migrations.RemoveField(
            model_name='socios',
            name='apellidos',
        ),
        migrations.RemoveField(
            model_name='socios',
            name='correo_electronico',
        ),
        migrations.RemoveField(
            model_name='socios',
            name='fecha_ingreso',
        ),
        migrations.RemoveField(
            model_name='socios',
            name='nombres',
        ),
        migrations.RemoveField(
            model_name='socios',
            name='password',
        ),
        migrations.RemoveField(
            model_name='socios',
            name='usuario',
        ),
        migrations.AddField(
            model_name='socios',
            name='user',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='socio', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='socios',
            name='aporte',
            field=models.DecimalField(decimal_places=2, max_digits=8),
        ),
        migrations.AlterField(
            model_name='socios',
            name='categoria',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='socios',
            name='cedula',
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='socios',
            name='dedicacion_academica',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='socios',
            name='direccion_domiciliaria',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='socios',
            name='facultad',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='socios',
            name='fecha_nacimiento',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='socios',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='socios',
            name='lugar_nacimiento',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='socios',
            name='numero_convencional',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='socios',
            name='numero_telefonico',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='socios',
            name='titulo',
            field=models.CharField(max_length=100),
        ),
    ]
