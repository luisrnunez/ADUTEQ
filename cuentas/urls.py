from django.urls import path
from .views import cuentas,reportes_cuentas_mensuales,obtener_informacion_prestamos, obtener_comision_descuentos, obtener_comision_descuentos_cuotas

urlpatterns = [
    path('cuentas/', cuentas, name='cuentas'),
    path('reportes_cuentas_mensuales/', reportes_cuentas_mensuales, name='reportes_cuentas_mensuales'),
    path('obtener_informacion_prestamos/<int:mes>/<int:anio>/', obtener_informacion_prestamos, name='obtener_informacion_prestamos'),
    path('obtener_comision_descuentos/<int:mes>/<int:anio>/', obtener_comision_descuentos, name='obtener_comision_descuentos'),
    path('obtener_comision_descuentos_cuotas/<int:mes>/<int:anio>/', obtener_comision_descuentos_cuotas, name='obtener_comision_descuentos_cuotas'),
]
