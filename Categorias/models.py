from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Categorias(models.Model):
    nombre_cat=models.CharField(max_length=100)
    descripcion=models.CharField(max_length=200, blank=True)