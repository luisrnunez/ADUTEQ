from django.db import models
from proveedores.models import Proveedor

# Create your models here.
class PagosProveedor(models.Model):
    proveedor=models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    valor_total=models.DecimalField(max_digits=8,decimal_places=2)
    fecha_creacion=models.DateField(null=True)
    fecha_pago=models.DateField(null=True)
    valor_cancelado=models.BooleanField(null=True)


