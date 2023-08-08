from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from django.utils import timezone
# Create your models here.

class Socios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='socio',default=1)
    cedula = models.CharField(max_length=10, unique=True)
    fecha_nacimiento = models.DateTimeField()
    lugar_nacimiento = models.CharField(max_length=100)
    numero_telefonico = models.CharField(max_length=20,unique=True,blank=True,null=True)
    numero_convencional = models.CharField(max_length=20,unique=True,blank=True,null=True)
    direccion_domiciliaria = models.CharField(max_length=100)
    facultad = models.CharField(max_length=100,null=True,blank=True)
    categoria = models.CharField(max_length=100)
    dedicacion_academica = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(null=True, blank=True)
    aporte = models.DecimalField(max_digits=8,decimal_places=2)

    def __str__(self):
        return self.user.first_name
    
class Aportaciones(models.Model):
    TIPOS_APORTACION = (
        ('AE', 'Ayuda Económica'),
        ('CO', 'Cuota Ordinaria'),
    )

    socio = models.ForeignKey(Socios, on_delete=models.CASCADE)
    tipo_aportacion = models.CharField(max_length=2, choices=TIPOS_APORTACION)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateField(null=True)

# @receiver(post_save, sender=Socios)
# def agregar_aportaciones_nuevo_socio(sender, instance, created, **kwargs):
#     if created:
#         # Agregar las aportaciones al nuevo socio
#         Aportaciones.objects.create(socio=instance, tipo_aportacion='AE', monto=3, fecha=date.today())
#         Aportaciones.objects.create(socio=instance, tipo_aportacion='CO', monto=10, fecha=date.today())