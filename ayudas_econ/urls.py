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

    path('eliminarayuda/<int:codigo>', views.deleteAyuda),

]