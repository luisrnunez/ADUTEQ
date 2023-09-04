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
    path('busquedadetallescupos/', views.busqueda_detalles_cupos, name='searchcupo'),

    path('prueba/', views.prueba),
    #------------------------------------------------------------
    path('verdetallescupo/<int:proveedor_id>', views.verdetallescupos),
    path('editcupos/<int:codigo>', views.editCupos, name='editarcupos'),
    path('actualizarcupos/', views.editarcupos, name='actualizar_cupos'),
    path('agregarCuenta/<int:codigo>', views.agregarCuenta,name='agregarCuenta'),
    path('agregarnuevacuenta/<int:codigo>', views.agregarnuevacuenta,name='agregarnuevacuenta'),
    path('agregarnuevacuentabancaria/<int:codigo>', views.agregarnuevacuentabancaria,name='agregarnuevacuentabancaria'),

    path('eliminarcuenta/<int:codigo>/<int:prov>', views.eliminarcuenta,name='eliminarcuenta'),
]