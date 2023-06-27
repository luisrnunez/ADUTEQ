from django.db import models

# Create your models here.

class Socios(models.Model):
    usuario = models.CharField(max_length=50,default='user')
    password = models.CharField(max_length=20,default='123')
    cedula = models.CharField(max_length=10,default='1250259114')
    nombres = models.CharField(max_length=100,default='Jose')
    apellidos = models.CharField(max_length=100,default='Nuñez')
    fecha_nacimiento = models.DateField(default='13/03/2001')
    lugar_nacimiento = models.CharField(max_length=100,default='Quito')
    correo_electronico = models.EmailField(default='user@gmail.com')
    numero_telefonico = models.CharField(max_length=20,default='0960138819')
    numero_convencional = models.CharField(max_length=20,default='0960138819')
    direccion_domiciliaria = models.CharField(max_length=100,default='SANTO')
    facultad = models.CharField(max_length=100,default='FCI')
    categoria = models.CharField(max_length=100,default='Titular')
    dedicacion_academica = models.CharField(max_length=100,default='INGENIERIA')
    fecha_ingreso = models.DateField(default='2012')
    titulo = models.CharField(max_length=100,default='INGENIERO ELECTRICO')
    foto = models.BinaryField(null=True, blank=True)
    aporte = models.CharField(max_length=5,default='13')
    activo = models.BooleanField(default=True)
 

class Admin(models.Model):
    usuario = models.CharField(max_length=50,default='user')
    password = models.CharField(max_length=20,default='123')