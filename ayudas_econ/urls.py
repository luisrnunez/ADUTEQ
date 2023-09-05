from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('motivos/', views.motivos),
    path('formotivos/', views.formRegistro),
    path('aggmotivos/', views.aggMotivo),
    #Editar motivos
    #abrir form editar
    path('editmotivo/<int:codigo>', views.feditMotivo),
    #guardarcambios
    path('geditmotivo/', views.editarmotivo),
    #Eliminar motivo
    path('eliminarmotivo/<int:codigo>', views.deleteMotivo),


    path('verayudas/', views.viewayudas,name='lista_ayudas'),
    path('formAggAyuda/', views.formRegistroAyuda),
    path('aggAyuda/', views.aggAyuda),

    path('formeditarayuda/<int:codigo>', views.feditAyuda),

    path('eliminarayuda/<int:codigo>', views.eliminar_ayuda),

    path('guardar_aportacion/<int:detalle_id>/', views.guardar_aportacion, name='guardar_aportacion'),
    path('verificar_socio/<int:detalle_id>/', views.verificar_socio, name='verificar_socio'),
    #detallesayuda
    path('buscar_detalle/', views.buscar_detalle, name='buscar_detalle'),
    path('detalleayuda/<int:ayuda_id>', views.detallesAyuda),
    path('registrarayuda/<int:detalle_id>/<int:valor>/', views.registro_ayuda),
    path('prestamo2/presagregar_pdf/<int:det_id>/',views.presagregar_pdf2, name = 'presagregar_pdf'),

]