from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from django.utils import timezone
from Categorias.models import Categorias,Facultades,Titulos,DedicacionAcademica
from django.db import connection
from Periodo.models import Periodo,AjustesSistema
# Create your models here.

class Socios(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='socio',default=1)
    cedula = models.CharField(max_length=10, unique=True)
    fecha_nacimiento = models.DateTimeField(unique=False,blank=True,null=True)
    lugar_nacimiento = models.CharField(max_length=100,unique=False,blank=True,null=True)
    numero_telefonico = models.CharField(max_length=20,unique=False,blank=True,null=True)
    numero_convencional = models.CharField(max_length=20,unique=False,blank=True,null=True)
    direccion_domiciliaria = models.CharField(max_length=100)
    facultad = models.CharField(max_length=100,null=True,blank=True)
    categoria = models.CharField(max_length=100)
    dedicacion_academica = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(null=True, blank=True)
    aporte = models.DecimalField(max_digits=8,decimal_places=2)

    def __str__(self):
        return self.user.first_name
    class Meta:
        ordering = ['user__last_name']
    
class Aportaciones(models.Model):
    TIPOS_APORTACION = (
        ('AE', 'Ayuda Económica'),
        ('CO', 'Cuota Ordinaria'),
    )

    socio = models.ForeignKey(Socios, on_delete=models.CASCADE)
    tipo_aportacion = models.CharField(max_length=2, choices=TIPOS_APORTACION)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    fecha = models.DateField(null=True)

class Total_Ayuda_Permanente(models.Model):
    tipo_aportacion = models.CharField(max_length=2, primary_key=True)
    total_actual = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_transaccion = models.DateField()

class Total_Cuota_Ordinaria(models.Model):
    tipo_aportacion = models.CharField(max_length=2, primary_key=True)
    total_actual = models.DecimalField(max_digits=8, decimal_places=2)
    fecha_transaccion = models.DateField()


# @receiver(post_save, sender=Socios)
# def agregar_aportaciones_nuevo_socio(sender, instance, created, **kwargs):
#     if created:
#         # Agregar las aportaciones al nuevo socio
#         Aportaciones.objects.create(socio=instance, tipo_aportacion='AE', monto=3, fecha=date.today())
#         Aportaciones.objects.create(socio=instance, tipo_aportacion='CO', monto=10, fecha=date.today())

def obtener_datos_socioss(socio_id, mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM nuevo_obtener_datos({socio_id}, {mes}, {anio});"
        )
        resultados = cursor.fetchall()
    
    if resultados:
        column_names = [
            'nombre', 'cedula', 'cuota_prestamos', 'aportacion',
            'descuento_proveedores', 'aportacion_ayudaseco', 'total'
        ]
        resultado_dict = dict(zip(column_names, resultados[0]))
        return resultado_dict
    else:
        return None
    
def datos_para_el_pdf(socio_id, mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM obtener_consumos_por_proveedor({socio_id}, {mes}, {anio});")
        consumos_proveedor = cursor.fetchall()

        cursor.execute(f"SELECT * FROM obtener_cuotas_pagadas({socio_id}, {mes}, {anio});")
        consumos_cuotas = cursor.fetchall()

        cursor.execute(f"SELECT * FROM obtener_aportacion_socio({socio_id}, {mes}, {anio});")
        aportaciones_socio = cursor.fetchall()

        cursor.execute(f"SELECT * FROM obtener_info_ayuda_economica({socio_id}, {mes}, {anio});")
        aportaciones_ayuda = cursor.fetchall()

        cursor.execute(f"SELECT * FROM obtener_informe_mensual2({socio_id}, {mes}, {anio});")
        consumo_total = cursor.fetchall()

    return consumos_proveedor, consumos_cuotas, aportaciones_socio, aportaciones_ayuda, consumo_total