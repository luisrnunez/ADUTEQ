from django.urls import path
from .views import cuentas

urlpatterns = [
    path('cuentas/', cuentas, name='cuentas')
]
