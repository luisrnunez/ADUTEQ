from django.urls import path
from .views import lista_pagosp,aplicar_pago

urlpatterns = [
    path('listar_pagosp/',lista_pagosp, name = 'lista_pagosp'),
    path('aplicar_pago/<int:PagosProveedor_id>/<int:valor>/',aplicar_pago, name = 'lista_pagosp')
]