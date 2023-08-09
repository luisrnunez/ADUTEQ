from django.urls import path
from .views import enviar_correo_todoss, enviar_correo_uno, nuevo_enviar_correo

urlpatterns = [

    path('enviar_gastos/<int:socio_id>/', nuevo_enviar_correo, name='enviar_gastos'),
    # correo para todos
    path('enviar_gastos_todos/', enviar_correo_todoss, name='enviar_gastos_todos'),
]