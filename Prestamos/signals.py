from django.db import models
from . import models
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=models.PagoMensual)
def actualizar_estado_prestamo(sender, instance, **kwargs):
    prestamo = models.Prestamo
    todas_cuotas_pagadas = prestamo.pagomensual_set.filter(cancelado=False).count() == 0
    prestamo.cancelado = todas_cuotas_pagadas
    prestamo.save()