from django.urls import path
from .views import guardar_pago_cuota, guardar_prestamo, mostrar_prestamo,editar_prestamo,aplicar_pago, mostrar_detalles,mostrar_detalles_todo, aplicar_pago_cuota, eliminar_prestamo_y_cuotas, editar_detalles, presagregar_pdf, editar_evidencia

urlpatterns = [
    path('prestamo/guardar/', guardar_prestamo, name='guardar_prestamo'),
    path('prestamos/', mostrar_prestamo, name='mostrar_prestamo'),
    path('prestamo/editar/<int:prestamo_id>/', editar_prestamo, name='editar_prestamo'),
    path('prestamo/aplicar_pago/<int:prestamo_id>/<int:valor>/',aplicar_pago, name = 'aplicar_pago'),

    path('prestamo/presagregar_pdf/<int:det_id>/',presagregar_pdf, name = 'presagregar_pdf'),
    path('prestamo/editar_evidencia/<int:prestamo_id>/',editar_evidencia, name = 'editar_evidencia'),

    path('detalles_pago/<int:socio_id>/<int:prestamo_id>', mostrar_detalles , name='mostrar_detalles_pago'),
    path('detalles_pago/all/', mostrar_detalles_todo , name='mostrar_detalles_todo'),
    path('prestamo/cuota/', guardar_pago_cuota, name='guardar_cuota'),
    path('editar_detalles/<int:detalle_id>/<int:socio_id>/<int:prestamo_id>', editar_detalles, name='editar_detalles'),
    path('prestamo_eliminar/<int:prestamo_id>', eliminar_prestamo_y_cuotas, name='eliminar_prestamo'),
    path('prestamo/aplicar_pago_cuota/<int:cuota_id>/<int:valor>/<int:socio_id>/<int:prestamo_id>/',aplicar_pago_cuota, name = 'aplicar_pago_cuota'),
]
