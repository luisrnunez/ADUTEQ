from django.db import models
from socios.models import Socios
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from Periodo.models import Periodo
import os


def upload_to_evidencia(instance, filename):
    # 'instance' es la instancia del modelo (Detalle_cuotas) que se está creando o modificando.
    # 'filename' es el nombre original del archivo.

    # Obtenemos la extensión del archivo (por ejemplo, .pdf)
    extension = os.path.splitext(filename)[1]

    # Definimos el nombre del archivo que se almacenará en la carpeta 'evidencias'
    # Aquí podrías utilizar algún identificador único de la instancia para evitar colisiones de nombres.
    nuevo_nombre = f'evidencia_{instance.id}{extension}'

    # Devolvemos la ruta relativa dentro de la carpeta 'evidencias'
    return os.path.join('evidenciaspres', nuevo_nombre)


class Prestamo(models.Model):
    socio = models.ForeignKey(Socios, on_delete=models.CASCADE)
    tipo= models.BooleanField(default=False)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_primer_pago = models.DateField(null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(null=True)
    plazo_meses = models.PositiveIntegerField()
    tasa_interes = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    descripcion = models.TextField(blank=True, null=True)
    evidencia=models.FileField(upload_to=upload_to_evidencia, blank=True, null=True)
    cancelado = models.BooleanField(default=False)

    def __str__(self):
        return f"Prestamo de {self.monto} a {self.socio.user.first_name} {self.socio.user.last_name}"



class PagoMensual(models.Model):
    socio = models.ForeignKey(Socios, on_delete=models.CASCADE)
    prestamo=models.ForeignKey(Prestamo, on_delete=models.CASCADE)
    numero_cuota = models.PositiveIntegerField()
    monto_pago = models.DecimalField(max_digits=8, decimal_places=2)
    evidencia=models.FileField(upload_to=upload_to_evidencia, blank=True, null=True)
    cancelado = models.BooleanField(default=False)
    fecha_pago = models.DateField()

    def __str__(self):
        return f"Pago de {self.monto_pago} a {self.socio.user.first_name} {self.socio.user.last_name}"
    

@receiver(post_save, sender=PagoMensual) 
def actualizar_estado_prestamo(sender, instance, **kwargs):
    prestamos = instance.prestamo
    #todas_cuotas_pagadas = prestamos.pagomensual_set.filter(cancelado=False).count() == 0
    todas_cuotas_pagadas = prestamos.pagomensual_set.filter(cancelado=False).exists()
    prestamos.cancelado = not todas_cuotas_pagadas
    prestamos.fecha_pago=date.today()
    prestamos.save()

post_save.connect(actualizar_estado_prestamo, sender=PagoMensual)

