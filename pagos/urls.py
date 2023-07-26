from django.urls import path
from .views import lista_pagos,agrefar_pagos,editar_pago,eliminar_pago,extraer_datos_pdf,extraer_descuentos,guardar_descuentos_prov
from .views import lista_pagos_cuotas,agregar_pagos_cuotas,detalles_cuota,registra_pago_cuota,eliminar_pago_cuota,agregar_pdf

urlpatterns = [
    path('listar_pagos/',lista_pagos),
    path('lista_pagos_cuotas/',lista_pagos_cuotas),
    path('agregar_pago/',agrefar_pagos),
    path('agregar_pagos_cuotas/',agregar_pagos_cuotas),
    path('editar_pago/<int:pago_id>/',editar_pago, name='editarpago'),

    path('detalles_cuota/<int:pago_cuota_id>/',detalles_cuota, name='detalles_cuota'),
    path('registra_pago_cuota/<int:det_cuo_id>/',registra_pago_cuota, name='registra_pago_cuota'),
    path('eliminar_pago_cuota/<int:det_cuo_id>/',eliminar_pago_cuota, name='eliminar_pago_cuota'),
    path('agregar_pdf/<int:det_id>/',agregar_pdf, name='agregar_pdf'),

    path('eliminar_pago/<int:pago_id>/',eliminar_pago, name='eliminarpago'),
    path('extraer_pdf/', extraer_datos_pdf, name='extraer_pdf'),
    path('extraer_descuentos/', extraer_descuentos, name='extraer_descuentos'),
    path('guardar_descuentos_prov/<int:id>/<str:fecha>/', guardar_descuentos_prov, name='guardar_descuentos_prov'),
]