# import schedule
# import time

# from django.utils import timezone
# from socios.models import Aportaciones, Socios
# from datetime import datetime

# def registrar_aportaciones_mensuales():
#     socios = Socios.objects.all()

#     hoy = timezone.now().date()
#     primer_dia_mes_actual = hoy.replace(day=1)

#     for socio in socios:
#         aportaciones_ultimo_mes = Aportaciones.objects.filter(
#             socio=socio,
#             fecha__gte=primer_dia_mes_actual
#         )

#         if not aportaciones_ultimo_mes.exists() and socio.user.is_active:
#             transaccion_ae = Aportaciones.objects.create(
#                 socio=socio,
#                 tipo_aportacion='AE',
#                 monto=3,  # Monto de Ayuda Económica
#                 fecha=hoy
#             )

#             transaccion_co = Aportaciones.objects.create(
#                 socio=socio,
#                 tipo_aportacion='CO',
#                 monto=10,  # Monto de Cuota Ordinaria
#                 fecha=hoy
#             )

# # Programa la tarea para ejecutarse el 1ro de cada mes a las 12:00 AM
# schedule.every().day.at("00:00").do(registrar_aportaciones_mensuales)

# while True:
#     schedule.run_pending()
#     time.sleep(1)