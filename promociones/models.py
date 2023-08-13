from django.db import models
from django.db import models
from django.utils import timezone
from proveedores.models import Proveedor

# Create your models here.
class Promocion(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=300)
    imagen = models.ImageField(null=True, blank=True)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo