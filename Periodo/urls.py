from django.urls import path
from .views import mostrar_ajustes,agregar_periodo,cerrar_periodo,guardar_cierre_automatico

urlpatterns = [
  
    path('ajustes/', mostrar_ajustes, name='mostrar_ajustes'),
    path('guardar/periodo/', agregar_periodo, name='agregar_periodo'),
    path('cerrar/periodo/', cerrar_periodo, name='cerrar_periodo'),
    path('guardar_cierre_automatico/', guardar_cierre_automatico, name='guardar_cierre_automatico'),
    # ...
]