from django.urls import path
from .views import enviar_correo_todos, nuevo_enviar_correo,reportes, generar_reporte_pdf_total_usuarios,cerrar_periodo,actualizar_cancelados,actualizar_estados, actualizar_descuentos,generar_reporte_consumo_todos, reportes_socios_general
from .views import reportes_datos_socios, actualizar_estados_ayudas,generar_pdf_socio, reporte_genero,actualizar_estados_ayudas_exter,obtener_consumos_por_proveedor,resultados_consulta,resultados_consulta_cuotas
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [ 

    path('enviar_gastos/<int:socio_id>/', nuevo_enviar_correo, name='enviar_gastos'),
    # correo para todos
    path('enviar_gastos_todos/', enviar_correo_todos, name='enviar_gastos_todos'),
    path('reportes/', reportes, name='reportes'),
    path('reportes_datos_socios/', reportes_datos_socios, name='reportes_datos_socios'),
    path('cerrar_periodo/', cerrar_periodo, name='cerrar_periodo'),
    path('reportes_socios/', generar_reporte_pdf_total_usuarios, name='reportes_socios'),
    path('actualizar_cancelados/', actualizar_cancelados, name='actualizar_cancelados'),
    path('actualizar_estados/', actualizar_estados, name='actualizar_estados'),
    path('actualizar_estados_ayudas/', actualizar_estados_ayudas, name='actualizar_estados_ayudas'),
    path('actualizar_estados_ayudas_exter/', actualizar_estados_ayudas_exter, name='actualizar_estados_ayudas_exter'),
    path('actualizar_descuentos/', actualizar_descuentos, name='actualizar_descuentos'),
    path('reportes_socios_todos/', generar_reporte_consumo_todos, name='reportes_socios_todos'),
    path('reportes_socios_general/', reportes_socios_general, name='reportes_socios_general'),
    path('generar_pdf_socio/', generar_pdf_socio, name='generar_pdf_socio'),
    path('reporte_genero/', reporte_genero, name='reporte_genero'),
    path('obtener_consumos_por_proveedor/', obtener_consumos_por_proveedor, name='obtener_consumos_por_proveedor'),
    path('resultados_consulta/', resultados_consulta, name='resultados_consulta'),
    path('resultados_consulta_cuotas/', resultados_consulta_cuotas, name='resultados_consulta_cuotas'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)