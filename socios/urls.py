from django.urls import path
from . import views

urlpatterns = [ 

    path('', views.login_),
    path('principal/', views.Principal, name='principal'),
    path('login/', views.Autenticacion_usuarios),
    path('actividades/', views.PanelActividades,name='actividades'),
    path('recuperacion/', views.Recuperar_cuenta),
    path('socios/', views.ListaSocios, name='listar_socios'),
    path('socios/agg/', views.AggSocio, name='agg_socios'),
    path('guardar_socio/', views.guardar_socio, name='guardar_socio'),
    path('editar_socio/<int:socio_id>/',views.editar_socio, name='editar_socio'),
    path('eliminar_socio/<int:user_id>/<int:valor>/', views.eliminar_socio, name='eliminar_socio'),
    path('buscar_socios/', views.buscar_socios, name='buscar_socios'),
    path('cerrar_sesion/', views.cerrar_sesion),
]
