from django.db import models
from socios.models import Socios
from Prestamos.models import upload_to_evidencia
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

# Create your models here.
class AyudasMot(models.Model):
    motivo=models.CharField(max_length=50)
    descripcion=models.TextField(max_length=200)
    def __str__(self):
        return self.motivo


class AyudasEconomicas(models.Model):
    socio=models.ForeignKey(Socios, on_delete=models.CASCADE, null=True)
    motivo=models.ForeignKey(AyudasMot, on_delete=models.CASCADE)
    descripcion=models.TextField(max_length=200)
    valorsocio=models.DecimalField(max_digits = 8, decimal_places = 2)
    fecha=models.DateTimeField()
    total=models.DecimalField(max_digits = 8, decimal_places = 2)
    evidencia=models.FileField(null=True)


class DetallesAyuda(models.Model):
    ayuda=models.ForeignKey(AyudasEconomicas, on_delete=models.CASCADE)
    socio=models.ForeignKey(Socios, on_delete=models.CASCADE)
    valor=models.DecimalField(max_digits = 8, decimal_places = 2)
    evidencia=models.FileField(upload_to=upload_to_evidencia, blank=True, null=True)
    fecha=models.DateTimeField(null=True)
    cancelado = models.BooleanField(default=False)

@receiver(post_save, sender=DetallesAyuda)
def actualizar_total_ayudas_economicas(sender, instance, **kwargs):
    if instance.cancelado:
        ayuda_economica = instance.ayuda
        detalles_cancelados = DetallesAyuda.objects.filter(ayuda=ayuda_economica, cancelado=True)
        total_cancelados = detalles_cancelados.aggregate(models.Sum('valor'))['valor__sum']
        ayuda_economica.total = total_cancelados or 0
        ayuda_economica.save()
post_save.connect(actualizar_total_ayudas_economicas, sender=DetallesAyuda)
