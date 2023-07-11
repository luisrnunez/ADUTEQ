from django.urls import path
from .views import enviar_correo, enviarGastoEmailTodos, enviar_correo_todos

urlpatterns = [

    path('enviar_gastos/<int:socio_id>/', enviar_correo, name='enviar_gastos'),
    # correo para todos
    path('enviar_gastos_todos/', enviar_correo_todos, name='enviar_gastos_todos'),
]