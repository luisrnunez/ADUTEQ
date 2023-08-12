from django.urls import path
from . import views 
from .views import SinAccesoView
from django.contrib.auth.decorators import login_required, user_passes_test



urlpatterns = [ 

    path('', views.login_),
    path('principal/',user_passes_test(views.is_superuser_or_staff,login_url='/sin-acceso/')(views.Principal),name='principal'),
    path('sin-acceso/',SinAccesoView.as_view(), name='sin_acceso'),
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
    #--------APORTACIONES---------
    path('aportaciones/', views.veraportaciones),
    path('aportaciones_socio/<int:socio_id>', views.veraportacionesocio),
    path('registraraportaciones/', views.registrar_aportaciones_mensuales),
    #--------CATEGORIAS DE SOCIOS--------------
    path('categoria/agregar/',views.agregar_categoria_socios,name="agregar_categoria_socios"),
    path('facultad/agregar/',views.agregar_facultad_socios,name="agregar_facultad_socios"),
    path('dedicacion/agregar/',views.agregar_dedicacion_socios,name="agregar_dedicacion_socios"),
    path('titulo/agregar/',views.agregar_titulo_socios,name="agregar_titulo_socios"),
    path('eliminar/facultad/', views.eliminar_facultad,name='eliminar_facultad'),
    path('eliminar/categoria/', views.eliminar_categoria,name='eliminar_categoria'),
    path('eliminar/dedicacion/', views.eliminar_dedicacion,name='eliminar_dedicacion'),
    path('eliminar/titulo/', views.eliminar_titulo,name='eliminar_titulo'),
]
