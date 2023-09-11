from django.contrib.humanize.templatetags.humanize import intcomma
from multiprocessing import context
from django.shortcuts import redirect, render
from Pagos.models import Pagos
from django.contrib import messages
from socios.models import Socios, Aportaciones, datos_para_el_pdf, obtener_datos_socioss
from proveedores.models import Proveedor
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from ayudas_econ.models import DetallesAyuda
from Pagos.models import Pagos_cuotas, Detalle_cuotas
from datetime import datetime, timedelta
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.contrib.auth.models import User
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Image
from django.http import JsonResponse
from django.db import connection
from xhtml2pdf import pisa
from io import BytesIO
from datetime import datetime
from django.template.loader import get_template
from django.template import Context
import os
import calendar

from Periodo.models import Periodo

# Create your views here.


def obtener_gastos_socio(socio_id):
    # Obtener el socio específico
    socio = Socios.objects.get(id=socio_id)

    # obtener la fecha del primer dia del mes actual
    hoy = datetime.today()
    primer_dia_mes_actual = hoy.replace(day=1) - timedelta(days=1)
    primer_dia_mes_actual = primer_dia_mes_actual.replace(day=1)

    print(primer_dia_mes_actual)

    # obtener todos los gastos de pagos del ultimo mes para el socio
    pagos_socio = Pagos.objects.filter(
        socio=socio, fecha_consumo__gte=primer_dia_mes_actual)
    gastos_por_proveedor = pagos_socio.values(
        'proveedor__nombre').annotate(total_proveedor=Sum('consumo_total'))

    # obtener todos los pagos de cuotas cancelados del ultimo mes para el socio
    pagos_cuotas_socio = Pagos_cuotas.objects.filter(
        socio=socio, estado=True, fecha_descuento__gte=primer_dia_mes_actual)

    gastos_por_proveedor_cuotas = Pagos_cuotas.objects.filter(socio_id=socio_id).values('proveedor__nombre', 'valor_cuota', 'fecha_descuento', 'numero_cuotas', 'cuota_actual').annotate(
        total_pago_cuota=Sum(ExpressionWrapper(F('valor_cuota'), output_field=DecimalField())))

    # obtener ayuda economic a la ue haya aportado el socio
    ayuda = DetallesAyuda.objects.filter(
        socio=socio, fecha__gte=primer_dia_mes_actual)

    # obtener todas las aportaciones del ultimo mes para el socio
    aportaciones_socio = Aportaciones.objects.filter(
        socio=socio, fecha__gte=primer_dia_mes_actual)

    ################################################################################
    # calcular el total general de gastos_por_proveedor
    total_gastos_proveedor = gastos_por_proveedor.aggregate(
        total_gastos=Sum('total_proveedor'))

    # calcular el total general de gastos_por_proveedor_cuotas
    total_gastos_proveedor_cuotas = gastos_por_proveedor_cuotas.aggregate(
        total_gastos_cuotas=Sum('total_pago_cuota'))

    # calcular el total general de aportaciones_socio
    total_aportaciones_socio = aportaciones_socio.aggregate(
        total_aportaciones=Sum('monto'))

    # calcular el total general de ayuda
    total_ayuda = ayuda.aggregate(total_ayuda=Sum('valor'))

    total_total = (total_gastos_proveedor['total_gastos'] or 0) + (total_gastos_proveedor_cuotas['total_gastos_cuotas'] or 0) + (
        total_aportaciones_socio['total_aportaciones'] or 0) + (total_ayuda['total_ayuda'] or 0)

    print(gastos_por_proveedor, gastos_por_proveedor_cuotas, aportaciones_socio, ayuda, total_gastos_proveedor,
          total_gastos_proveedor_cuotas, total_aportaciones_socio, total_ayuda, total_total)

    return gastos_por_proveedor, gastos_por_proveedor_cuotas, aportaciones_socio, ayuda, total_gastos_proveedor, total_gastos_proveedor_cuotas, total_aportaciones_socio, total_ayuda, total_total

# def enviar_datos_pdf(socio_id):
#     socio = Socios.objects.get(id=socio_id)
#     gastos_por_proveedor, gastos_por_proveedor_cuotas, aportaciones_socio, ayuda, total_gastos_proveedor,total_gastos_proveedor_cuotas,total_aportaciones_socio, total_ayuda, total_total = obtener_gastos_socio(socio_id)

#     context = {
#         'socio': socio,
#         'gastos_por_proveedor': str(gastos_por_proveedor),
#         'total_pagos_cuotas': str(gastos_por_proveedor_cuotas),
#         'aportaciones_socio': str(aportaciones_socio),
#         'ayudasEcon_socio': str(ayuda),

#         'total_gastos_proveedor': str(total_gastos_proveedor),
#         'total_gastos_proveedor_cuotas': str(total_gastos_proveedor_cuotas),
#         'total_aportaciones_socio': str(total_aportaciones_socio),
#         'total_ayuda': str(total_ayuda),
#         'total_total': str(total_total),
#     }

#     return context


def generar_pdf(context):
    template_path = 'info_detalle_pdf.html'
    template = get_template(template_path)
    html = template.render(context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        return result.getvalue()


def datospdf(socio_id, mes, anio):

    nombres_meses = [
        "-ENERO", "-FEBRERO", "-MARZO", "-ABRIL", "-MAYO", "-JUNIO",
        "-JULIO", "-AGOSTO", "-SEPTIEMBRE", "-OCTUBRE", "-NOVIEMBRE", "-DICIEMBRE"
    ]

    nombre_mes = nombres_meses[mes - 1]

    data = datos_para_el_pdf(socio_id, mes, anio)
    consumos_proveedor = data[0]
    consumos_cuotas = data[1]
    aportaciones_socio = data[2]
    aportaciones_ayuda = data[3]
    consumos_totales = data[4]

    hide_consumos_proveedor = any(
        consumo_total == 0 or consumo_total is None for _, consumo_total in consumos_proveedor)
    hide_consumos_cuotas = any(
        valor_cuota == 0 or valor_cuota is None for _, _, _, valor_cuota in consumos_cuotas)
    hide_aportaciones_socio = any(
        montoa == 0 or montoa is None for _, montoa in aportaciones_socio)
    hide_aportaciones_ayuda = any(
        valor_aportado == 0 or valor_aportado is None for _, valor_aportado in aportaciones_ayuda)
    # hide_consumos_totales = any(columna2 == 0 or columna2 is None for _, columna2 in consumos_totales)

    context = {
        'hide_consumos_proveedor': hide_consumos_proveedor,
        'hide_consumos_cuotas': hide_consumos_cuotas,
        'hide_aportaciones_socio': hide_aportaciones_socio,
        'hide_aportaciones_ayuda': hide_aportaciones_ayuda,
        # 'hide_consumos_totales': hide_consumos_totales,
        'consumos_proveedor': consumos_proveedor,
        'consumos_cuotas': consumos_cuotas,
        'aportaciones_socio': aportaciones_socio,
        'aportaciones_ayuda': aportaciones_ayuda,
        'consumos_totales': consumos_totales,
        'mes': nombre_mes
    }

    return context


########################## -------NUEVO ENVIAR CORREO------##############################

def nuevo_enviar_correo(request, socio_id):
    socio = Socios.objects.get(id=socio_id)
    hoy = datetime.today()

    numero_mes = hoy.month
    anio = hoy.year

    selected_mes = request.POST.get('mes', 'mes_actual')

    if selected_mes == 'mes_actual':
        numero_mes = hoy.month
        anio = hoy.year
    else:
        if hoy.month == 1:
            numero_mes = 12
        else:
            numero_mes = hoy.month - 1

        anio = hoy.year if numero_mes != 12 else hoy.year - 1

    resultados = obtener_datos_socioss(socio_id, numero_mes, anio)
    informe_data = generar_pdf(datospdf(socio_id, numero_mes, anio))

    if enviarGastoEmail(socio_id, resultados, informe_data):
        response = {'status': 'success',
                    'message': 'Informe enviado correctamente'}
    else:
        response = {'status': 'error', 'message': 'Ups. algo salió mal'}

    return JsonResponse(response)


################################### ---ENVIAR CORREO TODOS----############################


def enviarGastoEmail(socio_id, context, pdf_buffer):
    sociop = Socios.objects.get(id=socio_id)
    gastos = context
    # correo=render_to_string('gastosmensual.html', {"gastos": gastos})
    context = {'gastos': gastos}

    template = get_template('gastosmensual.html')
    content = template.render(context)
    email = EmailMultiAlternatives(
        'Informe mensual ADUTEQ',
        'Gastos',
        settings.EMAIL_HOST_USER,
        [sociop.user.email]
    )
    # email.attach_file("ADUTEQ\static\img\logo.png")
    email.attach_alternative(content, 'text/html')
    email.attach('informe.pdf', pdf_buffer, 'application/pdf')

    if sociop.user.is_active:
        email.send()
        return True
    else:
        return False


# def enviar_correo_todos(request):
#     selected_mes = request.POST.get('mes', 'mes_actual')  # Obtener el mes seleccionado del POST

#     hoy = datetime.today()
#     nombres_meses = [
#         "-ENERO", "-FEBRERO", "-MARZO", "-ABRIL", "-MAYO", "-JUNIO",
#         "-JULIO", "-AGOSTO", "-SEPTIEMBRE", "-OCTUBRE", "-NOVIEMBRE", "-DICIEMBRE"
#     ]

#     for socio in Socios.objects.all():
#         if socio.user.is_active:
#             try:
#                 if selected_mes == 'mes_actual':
#                     numero_mes = hoy.month
#                     anio = hoy.year
#                     nombre_mes = nombres_meses[numero_mes - 1]
#                 else:
#                     if hoy.month == 1:
#                         numero_mes = 12
#                     else:
#                         numero_mes = hoy.month - 1

#                     anio = hoy.year if numero_mes != 12 else hoy.year - 1
#                     nombre_mes = nombres_meses[numero_mes - 1]

#                 template = get_template('gastosmensual.html')
#                 resultados = obtener_datos_socioss(socio.id, numero_mes, anio)
#                 context = {'gastos': resultados}
#                 content = template.render(context)

#                 pdf_buffer = generar_pdf(datospdf(socio.id, numero_mes, anio))
#                 if pdf_buffer:
#                     email = EmailMultiAlternatives(
#                         'Informe mensual ADUTEQ ' + nombre_mes,
#                         'Gastos',
#                         settings.EMAIL_HOST_USER,
#                         [socio.user.email]
#                     )
#                     email.attach_alternative(content, 'text/html')
#                     email.attach('informe.pdf', pdf_buffer, 'application/pdf')
#                     email.send()
#             except Exception as e:
#                 print(str(e))
#     return JsonResponse({'status': 'success', 'message': 'Correos enviados a todos los socios'})

def enviar_correo_todos(request):
    # Obtener el mes seleccionado del POST
    selected_mes = request.POST.get('mes', 'mes_actual')

    hoy = datetime.today()
    nombres_meses = [
        "-ENERO", "-FEBRERO", "-MARZO", "-ABRIL", "-MAYO", "-JUNIO",
        "-JULIO", "-AGOSTO", "-SEPTIEMBRE", "-OCTUBRE", "-NOVIEMBRE", "-DICIEMBRE"
    ]

    # Divide la lista de socios en bloques de tamaño 'tamano_bloque'
    tamano_bloque = 25  # Puedes ajustar este valor según tus necesidades
    socios = Socios.objects.filter(user__is_active=True)
    bloques = [socios[i:i + tamano_bloque]
               for i in range(0, len(socios), tamano_bloque)]

    for bloque in bloques:
        for socio in bloque:
            try:
                if selected_mes == 'mes_actual':
                    numero_mes = hoy.month
                    anio = hoy.year
                    nombre_mes = nombres_meses[numero_mes - 1]
                else:
                    if hoy.month == 1:
                        numero_mes = 12
                    else:
                        numero_mes = hoy.month - 1

                    anio = hoy.year if numero_mes != 12 else hoy.year - 1
                    nombre_mes = nombres_meses[numero_mes - 1]

                template = get_template('gastosmensual.html')
                resultados = obtener_datos_socioss(socio.id, numero_mes, anio)
                context = {'gastos': resultados}
                content = template.render(context)

                pdf_buffer = generar_pdf(datospdf(socio.id, numero_mes, anio))
                if pdf_buffer:
                    email = EmailMultiAlternatives(
                        'Informe mensual ADUTEQ ' + nombre_mes,
                        'Gastos',
                        settings.EMAIL_HOST_USER,
                        [socio.user.email]
                    )
                    email.attach_alternative(content, 'text/html')
                    email.attach('informe.pdf', pdf_buffer, 'application/pdf')
                    email.send()
            except Exception as e:
                print(str(e))

    return JsonResponse({'status': 'success', 'message': 'Correos enviados a todos los socios'})


def reportes(request):
    periodo_seleccionado = Periodo.objects.filter(activo=True).first()
    socios = Socios.objects.all()
    return render(request, "reportes.html", {'periodo': periodo_seleccionado, 'socios': socios})


def obtener_consumo_total_func(mes, anio):

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM obtener_consumo_total_func({mes}, {anio});"
        )
        result = cursor.fetchall()
    return result


def obtener_consumo_total_todos_func(mes, anio):

    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM obtener_consumo_total_todos_func({mes}, {anio});"
        )
        result = cursor.fetchall()
    return result


def generar_reporte_pdf_total_usuarios(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_consumo_pendientes.pdf"'

    fecha_actual_str = request.POST.get('fecharpdps')
    fecha_actual = datetime.strptime(fecha_actual_str, '%Y-%m-%d')
    mes = fecha_actual.month
    anio = fecha_actual.year
    resultados = obtener_consumo_total_func(mes, anio)
    image_path = os.path.join(os.path.dirname(
        __file__), 'static', 'img', 'aduteq.png')
    total_consumo = obtener_suma_consumo_total_descuentos_func(mes, anio) or 0
    total_prestamo = obtener_suma_prestamo_total_func(mes, anio) or 0
    total_descuento_cuotas = obtener_suma_descuento_cuotas_func(mes, anio) or 0
    total_ayudas = obtener_suma_ayudas_func(mes, anio) or 0

    total = total_consumo + total_prestamo + total_descuento_cuotas + total_ayudas
    fecha_gen = datetime.now()

    template = get_template('reporte_total_consu.html')
    context = {'resultados': resultados,
               'mes': mes,
               'image_path': image_path,
               'anio': anio,
               'total': intcomma(total),
               'fecha_gen': fecha_gen
               }

    html = template.render(context)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response.write(result.getvalue())
        return response

    return HttpResponse("Error al generar el PDF", status=500)


def generar_reporte_consumo_todos(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_consumo_todos.pdf"'

        fecha_actual_str = request.POST.get('fecharpdts')
        fecha_actual = datetime.strptime(fecha_actual_str, '%Y-%m-%d')

        mes = fecha_actual.month
        anio = fecha_actual.year
        resultados = obtener_consumo_total_todos_func(mes, anio)
        image_path = os.path.join(os.path.dirname(
            __file__), 'static', 'img', 'aduteq.png')
        total = obtener_suma_total(mes, anio) or 0
        fecha_gen = datetime.now()

        template = get_template('reporte_consu_todos.html')
        context = {'resultados': resultados,
                   'mes': mes,
                   'image_path': image_path,
                   'anio': anio,
                   'total': intcomma(total),
                   'fecha_gen': fecha_gen
                   }

        html = template.render(context)
        result = BytesIO()

        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

        if not pdf.err:
            response.write(result.getvalue())
            return response

        return HttpResponse("Error al generar el PDF", status=500)
    else:
        return HttpResponse("Error al generar el PDF", status=500)


def cargar_imagen(path):
    imagen = Image(path)
    imagen.drawHeight = 50  # Ajusta la altura de la imagen
    imagen.drawWidth = 50   # Ajusta el ancho de la imagen
    return imagen


def cerrar_periodo(request):
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    if request.method == 'GET':
        consumos_proveedores = obtener_consumos_proveedores_func(mes, anio)
        suma_consumo = obtener_suma_consumo_total_descuentos_func(mes, anio)
        prestamos_cuotas = obtener_cuota_prestamos_func(mes, anio)
        suma_prestamos = obtener_suma_prestamo_total_func(mes, anio)
        descuento_cuotas = obtener_cuota_descuentos_func(mes, anio)
        suma_des_cuot = obtener_suma_descuento_cuotas_func(mes, anio)
        ayudas_des = obtener_ayudas_func(mes, anio)
        suma_ayudas = obtener_suma_ayudas_func(mes, anio)
        return render(request, "cerrar_periodo.html",
                      {'consumos_proveedores': consumos_proveedores, 'suma_consumo': suma_consumo,
                       'prestamos_cuotas': prestamos_cuotas, 'suma_prestamos': suma_prestamos,
                       'descuento_cuotas': descuento_cuotas, 'suma_des_cuot': suma_des_cuot,
                       'ayudas_des': ayudas_des, 'suma_ayudas': suma_ayudas})
    else:
        return render(request, 'login.html')


def obtener_consumos_proveedores_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM obtener_consumos_proveedores_func(%s, %s);", [mes, anio])
        results = cursor.fetchall()
    return results


def obtener_cuota_prestamos_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM obtener_cuota_prestamos_func(%s, %s);", [mes, anio])
        results = cursor.fetchall()
    return results


def obtener_cuota_descuentos_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM obtener_cuota_descuentos_func(%s, %s);", [mes, anio])
        results = cursor.fetchall()
    return results


def obtener_ayudas_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM obtener_ayudas_func(%s, %s);", [mes, anio])
        results = cursor.fetchall()
    return results


def actualizar_cancelados(request):
    checks = request.POST.getlist('socio_id[]')
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    with connection.cursor() as cursor:
        for id_socio in checks:
            cursor.execute(
                "SELECT * FROM actualizar_cancelados(%s, %s, %s);", [mes, anio, id_socio])
    return redirect(cerrar_periodo)

# def actualizar_cancelados(request):
#     fecha_actual = datetime.now()
#     mes = fecha_actual.month
#     anio = fecha_actual.year

#     prestamos_seleccionados = request.POST.getlist('prestamosSeleccionados[]')
#     print("Prestamos seleccionados:", prestamos_seleccionados)
#     with connection.cursor() as cursor:
#         for prestamo_id in prestamos_seleccionados:
#             cursor.execute("SELECT * FROM actualizar_cancelados(%s, %s, %s);", [mes, anio, prestamo_id])

#     return redirect(cerrar_periodo)


def actualizar_estados(request):
    checks = request.POST.getlist('socio_id[]1')
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    with connection.cursor() as cursor:
        for id_socio in checks:
            cursor.execute(
                "SELECT * FROM actualizar_estados(%s, %s, %s);", [mes, anio, id_socio])
    return redirect(cerrar_periodo)


def actualizar_estados_ayudas(request):
    checks = request.POST.getlist('ayuda_id[]')
    print(checks)
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    with connection.cursor() as cursor:
        for id_ayuda in checks:
            cursor.execute(
                "SELECT * FROM actualizar_estados_ayudas(%s, %s, %s);", [mes, anio, id_ayuda])
    return redirect(cerrar_periodo)


def actualizar_descuentos(request):
    checks = request.POST.getlist('pago_id[]')
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    with connection.cursor() as cursor:
        for id_pago in checks:
            cursor.execute(
                "SELECT * FROM actualizar_descuentos(%s, %s, %s);", [mes, anio, id_pago])
    return redirect(cerrar_periodo)


def obtener_suma_consumo_total_descuentos_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_suma_consumo_total_descuentos_func(%s, %s);", [mes, anio])
        suma_consumo = cursor.fetchone()[0]
    return suma_consumo


def obtener_suma_prestamo_total_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_suma_prestamo_total_func(%s, %s);", [mes, anio])
        suma_consumo = cursor.fetchone()[0]
    return suma_consumo


def obtener_suma_descuento_cuotas_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_suma_descuento_cuotas_func(%s, %s);", [mes, anio])
        suma_consumo = cursor.fetchone()[0]
    return suma_consumo


def obtener_suma_ayudas_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT obtener_suma_ayudas_func(%s, %s);", [mes, anio])
        suma_consumo = cursor.fetchone()[0]
    return suma_consumo


def llamar_cancelados(request):
    with connection.cursor() as cursor:
        cursor.callproc('actualizar_cancelados', [3, 8, 2023])


def obtener_suma_total(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT obtener_suma_total(%s, %s);", [mes, anio])
        suma_consumo = cursor.fetchone()[0]
    return suma_consumo


def reportes_socios_general(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_general_socios.pdf"'

    fecha_actual_str = request.POST.get('fecharpgds')
    fecha_actual = datetime.strptime(fecha_actual_str, '%Y-%m-%d')
    mes = fecha_actual.month
    anio = fecha_actual.year
    resultados = obtener_consumo_total_todos_func(mes, anio)
    image_path = os.path.join(os.path.dirname(
        __file__), 'static', 'img', 'aduteq.png')
    total = obtener_suma_total(mes, anio) or 0
    fecha_gen = datetime.now()

    template = get_template('reporte_general_socios.html')
    context = {'resultados': resultados,
               'mes': mes,
               'image_path': image_path,
               'anio': anio,
               'total': intcomma(total),
               'fecha_gen': fecha_gen
               }

    html = template.render(context)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response.write(result.getvalue())
        return response

    return HttpResponse("Error al generar el PDF", status=500)


def reportes_datos_socios(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_datos_socios.pdf"'

    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    socios = Socios.objects.filter(user__is_active=True).annotate(
        last_name=F('user__last_name')).order_by('last_name')
    image_path = os.path.join(os.path.dirname(
        __file__), 'static', 'img', 'aduteq.png')
    fecha_gen = datetime.now()

    template = get_template('datos_socios.html')
    context = {'socios': socios,
               'mes': mes,
               'image_path': image_path,
               'anio': anio,
               'fecha_gen': fecha_gen
               }

    html = template.render(context)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response.write(result.getvalue())
        return response

    return HttpResponse("Error al generar el PDF", status=500)


def generar_pdf_socio(request):
    socio_id = request.POST.get('socio')
    socio = Socios.objects.get(id=socio_id)
    template = get_template('odf_socio.html')
    context = {'socio': socio}

    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="socio_{socio.cedula}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF', status=500)

    return response
