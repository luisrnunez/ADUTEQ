from django.db import models

class Periodo(models.Model):
    anio = models.CharField(max_length=4)
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()   
    activo = models.BooleanField(default=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre
    

class AjustesSistema(models.Model):
    periodoAutomatico = models.BooleanField(default=True)
    dia_cierre = models.CharField(max_length=2,default=15) 
