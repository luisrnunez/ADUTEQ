from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Categorias(models.Model):
    nombre_cat=models.CharField(max_length=100)
    descripcion=models.CharField(max_length=200, blank=True)

class Facultades(models.Model):
    nombre_facu=models.CharField(max_length=500)
    descripcion=models.CharField(max_length=200, blank=True)

class DedicacionAcademica(models.Model):
    nombre_de=models.CharField(max_length=100)
    descripcion=models.CharField(max_length=200, blank=True)

class Titulos(models.Model):
    nombre_ti=models.CharField(max_length=100)
    descripcion=models.CharField(max_length=200, blank=True)