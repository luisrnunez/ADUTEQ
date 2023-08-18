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
    #detallesayuda
    path('detalleayuda/<int:ayuda_id>', views.detallesAyuda),
    path('registrarayuda/<int:detalle_id>/<int:valor>/', views.registro_ayuda),
<<<<<<< HEAD
    # path('prestamo/presagregar_pdf/<int:det_id>/',views.presagregar_pdf2, name = 'presagregar_pdf2'),
=======
    path('prestamo2/presagregar_pdf/<int:det_id>/',views.presagregar_pdf2, name = 'presagregar_pdf'),
>>>>>>> cde3a68da602feccd3bf8b767d51768a5c9531d0

]