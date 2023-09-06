import os
from django.db import models
from proveedores.models import Proveedor
from Periodo.models import Periodo

def upload_to_evidencia(instance, filename):
    # 'instance' es la instancia del modelo (Detalle_cuotas) que se está creando o modificando.
    # 'filename' es el nombre original del archivo.
    # Obtenemos la extensión del archivo (por ejemplo, .pdf)
    extension = os.path.splitext(filename)[1]
    # Definimos el nombre del archivo que se almacenará en la carpeta 'evidencias'
    # Aquí podrías utilizar algún identificador único de la instancia para evitar colisiones de nombres.
    nuevo_nombre = f'evidencia_{instance.id}{extension}'
    # Devolvemos la ruta relativa dentro de la carpeta 'evidencias'
    return os.path.join('evidencias_pagos_prov', nuevo_nombre)

# Create your models here.
class PagosProveedor(models.Model):
    proveedor=models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    valor_total=models.DecimalField(max_digits=8,decimal_places=2,null=True)
    comision=models.DecimalField(max_digits=8,decimal_places=2,null=True)
    fecha_creacion=models.DateField(null=True, blank=True)
    fecha_pago=models.DateField(null=True)
    valor_cancelado=models.BooleanField(null=True)
    evidencia=models.FileField(upload_to=upload_to_evidencia, blank=True, null=True)