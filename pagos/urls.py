from django.urls import path
from .views import lista_pagos,agrefar_pagos,editar_pago,eliminar_pago,extraer_datos_pdf

urlpatterns = [
    path('listar_pagos/',lista_pagos),
    path('agregar_pago/',agrefar_pagos),
    path('editar_pago/<int:pago_id>/',editar_pago, name='editarpago'),
    path('eliminar_pago/<int:pago_id>/',eliminar_pago, name='eliminarpago'),
    path('extraer_pdf/', extraer_datos_pdf, name='extraer_pdf'),
]