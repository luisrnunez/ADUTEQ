from django.urls import path
from .views import guardar_prestamo, mostrar_prestamo,editar_prestamo,aplicar_pago

urlpatterns = [
    path('prestamo/guardar/', guardar_prestamo, name='guardar_prestamo'),
    path('prestamos/', mostrar_prestamo, name='mostrar_prestamo'),
    path('prestamo/editar/<int:prestamo_id>/', editar_prestamo, name='editar_prestamo'),
    path('prestamo/aplicar_pago/<int:prestamo_id>/<int:valor>/',aplicar_pago, name = 'aplicar_pago')
]
