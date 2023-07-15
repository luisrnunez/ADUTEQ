from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Socios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='socio',default=1)
    cedula = models.CharField(max_length=10, unique=True)
    fecha_nacimiento = models.DateTimeField()
    lugar_nacimiento = models.CharField(max_length=100)
    numero_telefonico = models.CharField(max_length=20,unique=True,blank=True,null=True)
    numero_convencional = models.CharField(max_length=20,unique=True,blank=True,null=True)
    direccion_domiciliaria = models.CharField(max_length=100)
    facultad = models.CharField(max_length=100,null=True,blank=True)
    categoria = models.CharField(max_length=100)
    dedicacion_academica = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(null=True, blank=True)
    aporte = models.DecimalField(max_digits=8,decimal_places=2)

    def __str__(self):
        return self.user.username