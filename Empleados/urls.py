from django.urls import path
from . import views

urlpatterns = [

    path('empleados/', views.listar_empleados, name='listar_empleados'),
    path('guardar_empleado/', views.guardar_empleado, name='guardar_empleado'),
    path('empleado/agg/', views.agg_empleado, name='agg_empleado'),
    path('editar_empleado/<int:empleado_id>/',views.editar_empleado, name='editar_empleado'),
    path('eliminar_empleado/<int:empleado_id>/<int:valor>/', views.eliminar_empleado, name='eliminar_empleado')
]
