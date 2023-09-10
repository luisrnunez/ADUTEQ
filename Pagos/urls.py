from django.urls import path
from .views import lista_pagos,agrefar_pagos,editar_pago,eliminar_pago,extraer_datos_pdf,extraer_descuentos,guardar_descuentos_prov,agregar_pagos_cuotas_pen
from .views import lista_pagos_cuotas,agregar_pagos_cuotas,detalles_cuota,registra_pago_cuota,eliminar_pago_cuota,agregar_pdf, verificar_registros,convertir_cuotas,buscar_pagos_pendientes
from .views import generar_reporte_pdf,obtener_periodos_por_anio,buscar_pagos, listar_pagos_pendientes, agregar_pagos_pendiente,editar_pago_pendiente,eliminar_pago_pendiente
from .views import lista_pagos_cuotas_pendientes,detalles_cuota_pendiente,eliminar_pago_cuota_pendiente,registra_pago_cuota_pen,agregar_pdf2,convertir_cuotas2,principal_resumen


urlpatterns = [
    path('principal/resumen/', principal_resumen, name='principal_resumen'),
    path('listar_pagos/',lista_pagos, name='listar_pagos'),
    path('listar_pagos_pendientes/',listar_pagos_pendientes, name='listar_pagos_pendientes'),
    path('lista_pagos_cuotas/',lista_pagos_cuotas, name='listar_pagos_cuotas'),
    path('lista_pagos_cuotas_pendientes/',lista_pagos_cuotas_pendientes, name='lista_pagos_cuotas_pendientes'),
    path('agregar_pago/',agrefar_pagos),
    path('agregar_pagos_pendiente/',agregar_pagos_pendiente),
    path('agregar_pagos_cuotas/',agregar_pagos_cuotas),
    path('agregar_pagos_cuotas_pen/',agregar_pagos_cuotas_pen),
    path('editar_pago/<int:pago_id>/',editar_pago, name='editarpago'),
    path('editar_pago_pendiente/<int:pago_id>/',editar_pago_pendiente, name='editar_pago_pendiente'),

    path('detalles_cuota/<int:pago_cuota_id>/',detalles_cuota, name='detalles_cuota'),
    path('detalles_cuota_pendiente/<int:pago_cuota_id>/',detalles_cuota_pendiente, name='detalles_cuota_pendiente'),
    path('buscar_pagos/',buscar_pagos, name='buscar_pagos'),
    path('buscar_pagos_pendientes/',buscar_pagos_pendientes, name='buscar_pagos_pendientes'),
    path('registra_pago_cuota/<int:det_cuo_id>/',registra_pago_cuota, name='registra_pago_cuota'),
    path('registra_pago_cuota_pen/<int:det_cuo_id>/',registra_pago_cuota_pen, name='registra_pago_cuota_pen'),
    path('eliminar_pago_cuota/<int:det_cuo_id>/',eliminar_pago_cuota, name='eliminar_pago_cuota'),
    path('eliminar_pago_cuota_pendiente/<int:det_cuo_id>/',eliminar_pago_cuota_pendiente, name='eliminar_pago_cuota_pendiente'),
    path('agregar_pdf/<int:det_id>/',agregar_pdf, name='agregar_pdf'),
    path('agregar_pdf2/<int:det_id>/',agregar_pdf2, name='agregar_pdf2'),
    path('generar_reporte/', generar_reporte_pdf, name='generar_reporte'),

    path('verificar_registros/', verificar_registros, name='verificar_registros'),
    path('eliminar_pago/<int:pago_id>/',eliminar_pago, name='eliminarpago'),
    path('eliminar_pago_pendiente/<int:pago_id>/',eliminar_pago_pendiente, name='eliminar_pago_pendiente'),
    path('extraer_pdf/', extraer_datos_pdf, name='extraer_pdf'),
    path('extraer_descuentos/', extraer_descuentos, name='extraer_descuentos'),
    path('guardar_descuentos_prov/<int:id>/<str:fecha>/', guardar_descuentos_prov, name='guardar_descuentos_prov'),
    path('obtener_periodos/<int:anio>/',obtener_periodos_por_anio, name='obtener_periodos_por_anio'),
    path('convertir_cuotas/<int:pago_id>/', convertir_cuotas, name='convertir_cuotas'),
    path('convertir_cuotas2/<int:pago_id>/', convertir_cuotas2, name='convertir_cuotas2'),
]