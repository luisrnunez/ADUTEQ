from django.db import models
from django.db import models
from django.utils import timezone
from proveedores.models import Proveedor
import os

# Create your models here.

def upload_to_evidencia(instance, filename):
    # 'instance' es la instancia del modelo (Detalle_cuotas) que se está creando o modificando.
    # 'filename' es el nombre original del archivo.

    # Obtenemos la extensión del archivo (por ejemplo, .pdf)
    extension = os.path.splitext(filename)[1]

    # Definimos el nombre del archivo que se almacenará en la carpeta 'evidencias'
    # Aquí podrías utilizar algún identificador único de la instancia para evitar colisiones de nombres.
    nuevo_nombre = f'evidencia_{instance.id}{extension}'

    # Devolvemos la ruta relativa dentro de la carpeta 'evidencias'
    return os.path.join('evidenciaspro', nuevo_nombre)

class Promocion(models.Model):
    tipo=models.BooleanField(default=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=300)
    imagen = models.ImageField(null=True, blank=True)
    evidencia=models.FileField(upload_to=upload_to_evidencia, blank=True, null=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True)
    estado = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

