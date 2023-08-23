from django.urls import path
from .views import enviar_correo_todoss, nuevo_enviar_correo,reportes, generar_reporte_pdf_total_usuarios,cerrar_periodo,actualizar_cancelados,actualizar_estados, actualizar_descuentos

urlpatterns = [

    path('enviar_gastos/<int:socio_id>/', nuevo_enviar_correo, name='enviar_gastos'),
    # correo para todos
    path('enviar_gastos_todos/', enviar_correo_todoss, name='enviar_gastos_todos'),
    path('reportes/', reportes, name='reportes'),
    path('cerrar_periodo/', cerrar_periodo, name='cerrar_periodo'),
    path('reportes_socios/', generar_reporte_pdf_total_usuarios, name='reportes_socios'),
    path('actualizar_cancelados/', actualizar_cancelados, name='actualizar_cancelados'),
    path('actualizar_estados/', actualizar_estados, name='actualizar_estados'),
    path('actualizar_descuentos/', actualizar_descuentos, name='actualizar_descuentos'),
]