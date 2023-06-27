from django.db import models

# Create your models here.
class Proveedor(models.Model):
    nombre=models.CharField(max_length=200)
    telefono=models.CharField(max_length=13)
    RUC=models.CharField(max_length=13)
    direccion=models.CharField(max_length=500)
    comision=models.DecimalField(max_digits = 8, decimal_places = 2)
    estado=models.BooleanField(default=False)


    def __str__(self):
        return self.nombre