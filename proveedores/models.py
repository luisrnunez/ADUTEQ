from django.db import models
from socios.models import Socios
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from django.utils import timezone

# Create your models here.
class Proveedor(models.Model):
    nombre=models.CharField(max_length=200)
    telefono=models.CharField(max_length=13)
    ruc=models.CharField(unique=True,max_length=13)
    direccion=models.CharField(max_length=500)
    comision=models.IntegerField()
    cupo=models.DecimalField(max_digits = 8, decimal_places = 2) 
    estado=models.BooleanField(default=False)


    def __str__(self):
        return self.nombre
    class Meta:
        ordering = ['nombre']

class detallesCupos(models.Model):
    socio=models.ForeignKey(Socios, on_delete=models.CASCADE)
    proveedor=models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    cupo=models.DecimalField(max_digits = 8, decimal_places = 2)
    permanente=models.BooleanField(default=True)
    fechaccupo=models.DateField(null=True)

#SE ACTIVA AL CREAR UN PROVEEDOR CON EL FIN DE ASIGNAR EL CUPO A CADA SOCIO YA EXISTENTE
# @receiver(post_save, sender=Proveedor)
# def crear_detalles_cupos(sender, instance, created, **kwargs):
#     if created:
#         # Obtén el valor del cupo del proveedor recién creado
#         valor_cupo = instance.cupo

#         # Obtén todos los socios existentes
#         socios = Socios.objects.all()

#         # Crea un objeto detallesCupos para cada socio
#         for socio in socios:
#             detalles_cupos = detallesCupos(
#                 socio=socio,
#                 proveedor=instance,
#                 cupo=valor_cupo,
#                 fechaccupo=date.today()
#             )
#             detalles_cupos.save()
# post_save.connect(crear_detalles_cupos, sender=Proveedor)

# #SE ACTIVA AL ACTUALIZAR LOS CUPOS DE LOS PROVEEDORES
# @receiver(post_save, sender=Proveedor)
# def actualizar_cupo_detalles_cupos(sender, instance, **kwargs):
#     detalles_cupos = detallesCupos.objects.filter(proveedor=instance)

#     for detalle_cupo in detalles_cupos:
#         detalle_cupo.cupo = instance.cupo
#         detalle_cupo.fechaccupo=timezone.now().date()
#         detalle_cupo.save()
# post_save.connect(actualizar_cupo_detalles_cupos, sender=Proveedor)

#SE ACTIVA CADA QUE AGREGAMOS UN NUEVO SOCIO
# @receiver(post_save, sender=Socios)
# def crear_detalles_cupos_socios(sender, instance, created, **kwargs):
#     if created:
#         proveedores = Proveedor.objects.all()

#         for proveedor in proveedores:
#             detallesCupos.objects.create(
#                 socio=instance,
#                 proveedor=proveedor,
#                 cupo=proveedor.cupo,
#                 fechaccupo=timezone.now().date()
#             )
# post_save.connect(crear_detalles_cupos_socios, sender=Socios)



class CuentaBancaria(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    banco = models.CharField(max_length=100)
    numero_cuenta = models.CharField(max_length=50)
    tipo_cuenta = models.CharField(max_length=50)
    titular_cuenta = models.CharField(max_length=100)
    cedulaORuc = models.CharField(max_length=100)

    def __str__(self):
        return f"Cuenta de {self.proveedor.nombre} - {self.numero_cuenta}"