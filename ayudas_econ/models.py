from django.db import models    
from socios.models import Socios

# Create your models here.
class AyudasMot(models.Model):
    motivo=models.CharField(max_length=50)
    descripcion=models.TextField(max_length=200)
    def __str__(self):
        return self.motivo


class AyudasEconomicas(models.Model):
    socio=models.ForeignKey(Socios, on_delete=models.CASCADE)
    motivo=models.ForeignKey(AyudasMot, on_delete=models.CASCADE)
    descripcion=models.TextField(max_length=200)
    fecha=models.DateTimeField()
    total=models.DecimalField(max_digits = 8, decimal_places = 2)
    evidencia=models.FileField(null=True)
