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
    #detallesayuda
    path('buscar_detalle/<int:ayuda_id>', views.buscar_detalle, name='buscar_detalle'),
    path('detalleayuda/<int:ayuda_id>', views.detallesAyuda),
    path('registrarayuda/<int:detalle_id>/<int:valor>/', views.registro_ayuda),
    path('prestamo2/presagregar_pdf/<int:det_id>/',views.presagregar_pdf2, name = 'presagregar_pdf'),

    path('registrar_aportacion_externa/<int:detalle_id>/', views.registrar_aportacion_externa ,name='registrar_aportacion_externa'),
    path('obtener_ayudas_externas/<int:detalle_id>/', views.obtener_ayudas_externas, name='obtener_ayudas_externas'),
    path('editar_evidencia_ayuda/<int:ayuda_id>/', views.editar_evidencia_ayuda, name='editar_evidencia_ayuda'),

    #-----cuotas ordinarias------
    path('lista_cuotas_ordinarias/', views.listar_gastos_cuotas_ordinaria, name='listar_gastos_co'),
    path('registrar_consumo_ordinario/', views.registrar_consumo_ordinaria, name='registrar_co'),
    path('editar_evidencia_ordinaria/<int:consumo_id>/', views.editar_evidencia_consumo, name='editar_evidencia_consumo'),
    path('delete_consumo/<int:consumo_id>/', views.deleteConsumo, name='delete_consumo'),


]