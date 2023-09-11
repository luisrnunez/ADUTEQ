from django.db import models
from socios.models import Socios, Total_Ayuda_Permanente, Total_Cuota_Ordinaria
from Prestamos.models import upload_to_evidencia
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from Periodo.models import Periodo
from .models import Periodo
from django.template.loader import render_to_string
from django.db import connection
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
    valorsocio=models.DecimalField(max_digits = 8, decimal_places = 2, blank=True, null=True)
    fecha=models.DateField()
    total=models.DecimalField(max_digits = 8, decimal_places = 2)
    evidencia=models.FileField(null=True)

class DetallesAyuda(models.Model):
    ayuda=models.ForeignKey(AyudasEconomicas, on_delete=models.CASCADE)
    socio=models.ForeignKey(Socios, on_delete=models.CASCADE)
    valor=models.DecimalField(max_digits = 8, decimal_places = 2)
    evidencia=models.FileField(upload_to=upload_to_evidencia, blank=True, null=True)
    fecha=models.DateField(null=True)
    cancelado = models.BooleanField(default=False)
    pagado = models.BooleanField(default=False)

class AyudasExternas(models.Model):
    nombre=models.TextField(max_length=200)
    cedula=models.TextField(max_length=10)
    valor=models.DecimalField(max_digits = 8, decimal_places = 2)
    fecha=models.DateField()
    detalle=models.ForeignKey(AyudasEconomicas, on_delete=models.CASCADE)

class ConsumosCuotaOrdinaria(models.Model):
    descripcion=models.TextField(max_length=300)
    valor=models.DecimalField(max_digits = 8, decimal_places = 2)
    fecha=models.DateField()
    evidencia=models.FileField(upload_to=upload_to_evidencia, blank=True, null=True)


@receiver(post_save, sender=AyudasEconomicas)
def actualizar_total_ayuda_permanente(sender, instance, created, **kwargs):
    if created:
        # Obtener el objeto Total_Ayuda_Permanente (supongo que tienes solo un registro)
        total_ayuda_permanente = Total_Ayuda_Permanente.objects.get(tipo_aportacion='EA')

        # Restar el valor de la ayuda económica al total actual
        total_ayuda_permanente.total_actual -= instance.total
        total_ayuda_permanente.save()
post_save.connect(actualizar_total_ayuda_permanente, sender=AyudasEconomicas)

# @receiver(post_save, sender=DetallesAyuda)
# @receiver(post_save, sender=AyudasExternas)
# def actualizar_total_ayudas_economicas(sender, instance, **kwargs):
#     if isinstance(instance, DetallesAyuda) and instance.cancelado:
#         ayuda_economica = instance.ayuda
#         detalles_cancelados = DetallesAyuda.objects.filter(ayuda=ayuda_economica, cancelado=True)
#         total_cancelados = detalles_cancelados.aggregate(models.Sum('valor'))['valor__sum']
        
#         # Calcular el total de ayudas externas relacionadas con esta ayuda económica
#         total_ayudas_externas = AyudasExternas.objects.filter(detalle__in=detalles_cancelados).aggregate(models.Sum('valor'))['valor__sum']
        
#         # Sumar el total de ayudas externas al total cancelado
#         total_final = (total_cancelados or 0) + (total_ayudas_externas or 0)
        
#         ayuda_economica.total = total_final
#         ayuda_economica.save()
# post_save.connect(actualizar_total_ayudas_economicas, sender=DetallesAyuda)
# post_save.connect(actualizar_total_ayudas_economicas, sender=AyudasExternas)

def datos_para_ayuda():
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT tipo_aportacion, total_actual, fecha_transaccion FROM public.socios_total_ayuda_permanente;")
        total_ayuda_permanente = cursor.fetchall()

        cursor.execute(f"SELECT tipo_aportacion, total_actual, fecha_transaccion FROM public.socios_total_cuota_ordinaria;")
        total_cuota_ordinaria = cursor.fetchall()

    return total_ayuda_permanente, total_cuota_ordinaria
