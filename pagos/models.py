from django.db import models
from socios.models import Socios
from proveedores.models import Proveedor

# Create your models here.
class Pagos(models.Model):
    socio=models.ForeignKey(Socios, on_delete=models.CASCADE)
    proveedor=models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    consumo_total=models.DecimalField(max_digits=8,decimal_places=2)
    fecha_consumo=models.DateField()

