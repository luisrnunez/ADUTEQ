from django.urls import path
from .views import lista_pagosp,aplicar_pago,presagregar_pdf

urlpatterns = [
    path('listar_pagosp/',lista_pagosp,name='listar_pagosp'),
    path('aplicar_pago/<int:PagosProveedor_id>/<int:valor>/',aplicar_pago, name = 'registrar_pago'),
    path('pagosp/presagregar_pdf/<int:det_id>/',presagregar_pdf, name = 'prop_presagregar_pdf'),
]