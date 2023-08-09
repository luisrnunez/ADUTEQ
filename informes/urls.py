from django.urls import path
from .views import enviar_correo_todoss, enviar_correo_uno,reportes, generar_reporte_pdf_total_usuarios

urlpatterns = [

    path('enviar_gastos/<int:socio_id>/', enviar_correo_uno, name='enviar_gastos'),
    # correo para todos
    path('enviar_gastos_todos/', enviar_correo_todoss, name='enviar_gastos_todos'),
    
    path('reportes/', reportes, name='reportes'),

    path('reportes_socios/', generar_reporte_pdf_total_usuarios, name='reportes_socios'),
]