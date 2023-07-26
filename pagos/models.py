from django.db import models
from socios.models import Socios
from proveedores.models import Proveedor

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

class Detalle_cuotas(models.Model):
    pago_cuota=models.ForeignKey(Pagos_cuotas, on_delete=models.CASCADE)
    numero_cuota=models.IntegerField()
    estado = models.BooleanField(default=False)
    fecha_descuento=models.DateField()
    evidencia=models.FileField(blank=True)