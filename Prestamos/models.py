from django.db import models
from socios.models import Socios

class Prestamo(models.Model):
    socio = models.ForeignKey(Socios, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_pago = models.DateField(null=True)
    plazo_meses = models.PositiveIntegerField()
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2)
    descripcion = models.TextField(blank=True)
    cancelado = models.BooleanField(default=False)

    def __str__(self):
        return f"Prestamo de {self.monto} a {self.socio.nombres} {self.socio.apellidos}"
