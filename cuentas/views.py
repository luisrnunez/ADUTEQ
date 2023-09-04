import datetime
from io import BytesIO
import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from xhtml2pdf import pisa
from informes.views import obtener_suma_consumo_total_descuentos_func, obtener_suma_descuento_cuotas_func, obtener_suma_prestamo_total_func
from datetime import datetime
from django.db import connection


def cuentas(request):
    if request.method == 'POST':
        fecha_actual_str = request.POST.get('fechacuentas')
        fecha_actual = datetime.strptime(fecha_actual_str, '%Y-%m-%d')
        mes = fecha_actual.month
        anio = fecha_actual.year
        suma_consumo = obtener_suma_consumo_total_descuentos_Pagados_func(mes, anio) or 0
        suma_des_cuo = obtener_suma_descuento_cuotas_pagados_func(mes, anio) or 0
        suma_prestamos = obtener_suma_prestamo_total_Pagados_func(mes, anio) or 0
        sum_total = suma_prestamos+suma_consumo+suma_des_cuo
        comision_descuentos = obtener_total_comisiones(mes, anio) or 0
        comision_descuentos_cuotas = obtener_total_comisiones_desc(mes, anio) or 0
        suma_interes_prest = obtener_suma_intereses_prestamos(mes, anio) or 0
        total_com = comision_descuentos+comision_descuentos_cuotas+suma_interes_prest
        return render(request, 'cuentas_princ.html', {'suma_consumo': suma_consumo,
                                                      'suma_des_cuo': suma_des_cuo,
                                                      'suma_prestamos': suma_prestamos,
                                                      'sum_total': sum_total,
                                                      'comision_descuentos': comision_descuentos,
                                                      'comision_descuentos_cuotas': comision_descuentos_cuotas,
                                                      'suma_interes_prest': suma_interes_prest,
                                                      'fecha_actual': fecha_actual,
                                                      'mes': mes,
                                                      'anio': anio,
                                                      'total_com': total_com})
    else:
        fecha_actual = datetime.now()
        mes = fecha_actual.month
        anio = fecha_actual.year
        suma_consumo = obtener_suma_consumo_total_descuentos_Pagados_func(mes, anio) or 0
        suma_des_cuo = obtener_suma_descuento_cuotas_pagados_func(mes, anio) or 0
        suma_prestamos = obtener_suma_prestamo_total_Pagados_func(mes, anio) or 0
        sum_total = suma_prestamos+suma_consumo+suma_des_cuo
        comision_descuentos = obtener_total_comisiones(mes, anio) or 0
        comision_descuentos_cuotas = obtener_total_comisiones_desc(mes, anio) or 0
        suma_interes_prest = obtener_suma_intereses_prestamos(mes, anio) or 0
        total_com = comision_descuentos+comision_descuentos_cuotas+suma_interes_prest
        return render(request, 'cuentas_princ.html', {'suma_consumo': suma_consumo,
                                                      'suma_des_cuo': suma_des_cuo,
                                                      'suma_prestamos': suma_prestamos,
                                                      'sum_total': sum_total,
                                                      'comision_descuentos': comision_descuentos,
                                                      'comision_descuentos_cuotas': comision_descuentos_cuotas,
                                                      'suma_interes_prest': suma_interes_prest,
                                                      'fecha_actual': fecha_actual,
                                                      'mes': mes,
                                                      'anio': anio,
                                                      'total_com': total_com})


def obtener_total_comisiones(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_total_comisiones(%s, %s);", [mes, anio])
        suma_comision = cursor.fetchone()[0]
    return suma_comision

def obtener_suma_prestamo_total_Pagados_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_suma_prestamo_total_Pagados_func(%s, %s);", [mes, anio])
        suma_comision = cursor.fetchone()[0]
    return suma_comision

def obtener_suma_descuento_cuotas_pagados_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_suma_descuento_cuotas_pagados_func(%s, %s);", [mes, anio])
        suma_comision = cursor.fetchone()[0]
    return suma_comision

def obtener_suma_consumo_total_descuentos_Pagados_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_suma_consumo_total_descuentos_Pagados_func(%s, %s);", [mes, anio])
        suma_comision = cursor.fetchone()[0]
    return suma_comision


def obtener_total_comisiones_desc(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_total_comisiones_desc(%s, %s);", [mes, anio])
        suma_comision = cursor.fetchone()[0]
    return suma_comision


def obtener_suma_intereses_prestamos(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT obtener_suma_intereses_prestamos(%s, %s);", [mes, anio])
        suma_comision = cursor.fetchone()[0]
    return suma_comision


from django.http import JsonResponse

def obtener_informacion_prestamos(request, mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM obtener_informacion_prestamos(%s, %s);",
            [mes, anio]
        )
        resultados = cursor.fetchall()
    data = []
    for row in resultados:
        item = {
            'campo1': row[0],
            'campo2': row[1],
            'campo3': row[2]
        }
        data.append(item)

    return JsonResponse({'data': data})

def obtener_comision_descuentos(request, mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM obtener_comision_descuentos(%s, %s);",
            [mes, anio]
        )
        resultados = cursor.fetchall()
    data = []
    for row in resultados:
        item = {
            'campo1': row[0],
            'campo2': row[1],
            'campo3': row[2]
        }
        data.append(item)

    return JsonResponse({'data': data})

def obtener_comision_descuentos_cuotas(request, mes, anio):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM obtener_comision_descuentos_cuotas(%s, %s);",
            [mes, anio]
        )
        resultados = cursor.fetchall()
    data = []
    for row in resultados:
        item = {
            'campo1': row[0],
            'campo2': row[1],
            'campo3': row[2]
        }
        data.append(item)

    return JsonResponse({'data': data})




def reportes_cuentas_mensuales(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reportes_cuentas_mensuales.pdf"'

    mes = 9
    anio = 2023
    image_path = os.path.join(os.path.dirname(
        __file__), 'static', 'img', 'aduteq.png')
    # fecha_gen = datetime.now()

    template = get_template('cuentas_pdf.html')
    context = {
        'mes': mes,
        'image_path': image_path,
        'anio': anio,
        #    'fecha_gen': fecha_gen
    }

    html = template.render(context)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response.write(result.getvalue())
        return response

    return HttpResponse("Error al generar el PDF", status=500)
