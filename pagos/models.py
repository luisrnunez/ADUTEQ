from django.db import models
from socios.models import Socios
from proveedores.models import Proveedor
from Periodo.models import Periodo
import os

# Create your models here.
class Pagos(models.Model):
    socio=models.ForeignKey(Socios, on_delete=models.CASCADE)
    proveedor=models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    consumo_total=models.DecimalField(max_digits=8,decimal_places=2)
    fecha_consumo=models.DateField()

class Pagos_cuotas(models.Model):
    socio=models.ForeignKey(Socios, on_delete=models.CASCADE)
    proveedor=models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    numero_cuotas=models.IntegerField()
    cuota_actual=models.IntegerField()
    consumo_total=models.DecimalField(max_digits=8,decimal_places=2)
    valor_cuota=models.DecimalField(max_digits=8,decimal_places=2)
    estado = models.BooleanField(default=False)
    fecha_descuento=models.DateField()

def upload_to_evidencia(instance, filename):
    # 'instance' es la instancia del modelo (Detalle_cuotas) que se está creando o modificando.
    # 'filename' es el nombre original del archivo.

    # Obtenemos la extensión del archivo (por ejemplo, .pdf)
    extension = os.path.splitext(filename)[1]

    # Definimos el nombre del archivo que se almacenará en la carpeta 'evidencias'
    # Aquí podrías utilizar algún identificador único de la instancia para evitar colisiones de nombres.
    nuevo_nombre = f'evidencia_{instance.id}{extension}'

    # Devolvemos la ruta relativa dentro de la carpeta 'evidencias'
    return os.path.join('evidencias', nuevo_nombre)

class Detalle_cuotas(models.Model):
    pago_cuota=models.ForeignKey(Pagos_cuotas, on_delete=models.CASCADE)
    numero_cuota=models.IntegerField()
    estado = models.BooleanField(default=False)
    fecha_descuento=models.DateField()
    evidencia = models.FileField(upload_to=upload_to_evidencia, blank=True, null=True)