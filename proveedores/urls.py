from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('proveedores/', views.proveedor),
    path('aggproveedor/', views.formRegistro, name='guardarproveedor'),
    path('registrarproveedor/', views.aggProveedor),
    path('editProveedor/<int:codigo>', views.editProveedor),
    path('editarPro/', views.editarPro),
    path('deleteProveedor/<int:codigo>/<int:estado>/', views.deleteProveedor),

    path('verificarexiste/', views.verificarexi),
    #barra de busqueda
    path('busqueda/', views.busqueda, name='search'),

    path('prueba/', views.prueba),
]