from django.db import models
from django.contrib.auth.models import User
from Periodo.models import Periodo

# Create your models here.
class Empleado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cedula = models.CharField(max_length=10, default='1250259114', unique=True)
    nombres = models.CharField(max_length=100, default='Jose')
    apellidos = models.CharField(max_length=100, default='Nuñez')
    fecha_nacimiento = models.DateField(default='2001-03-13')
    correo_electronico = models.EmailField(default='user@gmail.com', unique=True)
    numero_telefonico = models.CharField(max_length=20, default='0960138819', unique=True)
    direccion_domiciliaria = models.CharField(max_length=100, default='SANTO')
    fecha_ingreso = models.DateField(default='2012-01-01')
    titulo = models.CharField(max_length=100, default='Contadora')
    activo = models.BooleanField(default=True)
 
