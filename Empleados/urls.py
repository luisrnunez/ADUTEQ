from django.urls import path
from . import views
from .views import actualizar_contra,restablecer_contra_emp,editar_perfil,info_empleado
urlpatterns = [
   
    path('empleados/', views.listar_empleados, name='listar_empleados'),
    path('guardar_empleado/', views.guardar_empleado, name='guardar_empleado'),
    path('empleado/agg/', views.agg_empleado, name='agg_empleado'),
    path('editar_empleado/<int:empleado_id>/',views.editar_empleado, name='editar_empleado'),
    path('eliminar_empleado/<int:empleado_id>/<int:valor>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('actualizar/', actualizar_contra, name='actualizar_contra'),
    path('actualizar/nueva/', restablecer_contra_emp, name='restablecer_contra_emp'),
    path('perfil/<int:empleado_id>/',info_empleado, name='info_empleado'),
    path('perfil/edit',editar_perfil, name='editar_perfil'),
   
]
