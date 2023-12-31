from django.urls import path
from .views import lista_pagos,agrefar_pagos,editar_pago,eliminar_pago,extraer_datos_pdf,extraer_descuentos,guardar_descuentos_prov
from .views import lista_pagos_cuotas,agregar_pagos_cuotas,detalles_cuota,registra_pago_cuota,eliminar_pago_cuota,agregar_pdf, verificar_registros,convertir_cuotas
from .views import generar_reporte_pdf,obtener_periodos_por_anio,buscar_pagos


urlpatterns = [
    path('listar_pagos/',lista_pagos, name='listar_pagos'),
    path('lista_pagos_cuotas/',lista_pagos_cuotas, name='listar_pagos_cuotas'),
    path('agregar_pago/',agrefar_pagos),
    path('agregar_pagos_cuotas/',agregar_pagos_cuotas),
    path('editar_pago/<int:pago_id>/',editar_pago, name='editarpago'),

    path('detalles_cuota/<int:pago_cuota_id>/',detalles_cuota, name='detalles_cuota'),
    path('buscar_pagos/',buscar_pagos, name='buscar_pagos'),
    path('registra_pago_cuota/<int:det_cuo_id>/',registra_pago_cuota, name='registra_pago_cuota'),
    path('eliminar_pago_cuota/<int:det_cuo_id>/',eliminar_pago_cuota, name='eliminar_pago_cuota'),
    path('agregar_pdf/<int:det_id>/',agregar_pdf, name='agregar_pdf'),
    path('generar_reporte/', generar_reporte_pdf, name='generar_reporte'),

    path('verificar_registros/', verificar_registros, name='verificar_registros'),
    path('eliminar_pago/<int:pago_id>/',eliminar_pago, name='eliminarpago'),
    path('extraer_pdf/', extraer_datos_pdf, name='extraer_pdf'),
    path('extraer_descuentos/', extraer_descuentos, name='extraer_descuentos'),
    path('guardar_descuentos_prov/<int:id>/<str:fecha>/', guardar_descuentos_prov, name='guardar_descuentos_prov'),
    path('obtener_periodos/<int:anio>/',obtener_periodos_por_anio, name='obtener_periodos_por_anio'),
    path('convertir_cuotas/<int:pago_id>/', convertir_cuotas, name='convertir_cuotas'),
]