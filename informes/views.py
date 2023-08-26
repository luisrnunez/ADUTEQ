from multiprocessing import context
from django.shortcuts import redirect,render
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
    pagos_socio = Pagos.objects.filter(socio=socio, fecha_consumo__gte=primer_dia_mes_actual)
    gastos_por_proveedor = pagos_socio.values('proveedor__nombre').annotate(total_proveedor=Sum('consumo_total'))

    # obtener todos los pagos de cuotas cancelados del ultimo mes para el socio
    pagos_cuotas_socio = Pagos_cuotas.objects.filter(socio=socio, estado=True, fecha_descuento__gte=primer_dia_mes_actual)

    gastos_por_proveedor_cuotas = Pagos_cuotas.objects.filter(socio_id=socio_id).values('proveedor__nombre','valor_cuota','fecha_descuento', 'numero_cuotas', 'cuota_actual').annotate(total_pago_cuota=Sum(ExpressionWrapper(F('valor_cuota'), output_field=DecimalField())))
    
    #obtener ayuda economic a la ue haya aportado el socio
    ayuda=DetallesAyuda.objects.filter(socio=socio, fecha__gte=primer_dia_mes_actual)

    # obtener todas las aportaciones del ultimo mes para el socio
    aportaciones_socio = Aportaciones.objects.filter(socio=socio, fecha__gte=primer_dia_mes_actual)

    ################################################################################
    # calcular el total general de gastos_por_proveedor
    total_gastos_proveedor = gastos_por_proveedor.aggregate(total_gastos=Sum('total_proveedor'))

    # calcular el total general de gastos_por_proveedor_cuotas
    total_gastos_proveedor_cuotas = gastos_por_proveedor_cuotas.aggregate(total_gastos_cuotas=Sum('total_pago_cuota'))

    # calcular el total general de aportaciones_socio
    total_aportaciones_socio = aportaciones_socio.aggregate(total_aportaciones=Sum('monto'))

    # calcular el total general de ayuda
    total_ayuda = ayuda.aggregate(total_ayuda=Sum('valor'))

    total_total = (total_gastos_proveedor['total_gastos'] or 0) + (total_gastos_proveedor_cuotas['total_gastos_cuotas'] or 0) + (total_aportaciones_socio['total_aportaciones'] or 0) + (total_ayuda['total_ayuda'] or 0)

    print(gastos_por_proveedor,gastos_por_proveedor_cuotas,aportaciones_socio,ayuda, total_gastos_proveedor, total_gastos_proveedor_cuotas,total_aportaciones_socio,total_ayuda,total_total)
    
    return gastos_por_proveedor, gastos_por_proveedor_cuotas, aportaciones_socio, ayuda,total_gastos_proveedor,total_gastos_proveedor_cuotas,total_aportaciones_socio, total_ayuda, total_total

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



def enviar_datos_pdf(socio_id):
    socio = Socios.objects.get(id=socio_id)
    hoy = datetime.today()

    image_path = r'ADUTEQ\static\img\aduteq.png'
    img = Image(image_path, width=100, height=100)  # Ajusta el tamaño de la imagen según tus necesidades
    img.hAlign = 'LEFT'
    img.vAlign = 'TOP'

    numero_mes = hoy.month
    anio = hoy.year
    consumos_proveedor, consumos_cuotas, aportaciones_socio, aportaciones_ayuda, consumos_totales = datos_para_el_pdf(socio.id, numero_mes, anio)

    # Procesar datos
    data = [
        ['Proveedor', 'Monto'],
    ] + [[str(proveedor), str(monto)] for proveedor, monto in consumos_proveedor]

    data_cuotas = [
        ['Fecha', 'Nombre', 'Cuota Actual', 'Valor'],
    ] + [[fecha.strftime("%Y-%m-%d"), str(proveedor), str(cuota), str(monto)] for fecha, proveedor, cuota, monto in consumos_cuotas]

    data_aportaciones = [
        ['Tipo', 'Monto'],
    ]
    for tipo, monto in aportaciones_socio:
        if tipo == 'AE':
            tipo = 'Ayuda Permanente'
        elif tipo == 'CO':
            tipo = 'Cuota Ordinaria'
        else:
            tipo = 'Total'
        data_aportaciones.append([str(tipo), str(monto)])

    data_ayuda = [
        ['Descripción', 'Monto'],
    ] + [[str(descripcion), str(monto)] for descripcion, monto in aportaciones_ayuda]

    data_general=[
        ['Motivo','Monto']
    ]
    for motivo, monto in consumos_totales:
        if motivo == 'AE':
            motivo = 'Ayuda Permanente'
        elif motivo == 'CO':
            motivo = 'Cuota Ordinaria'
        data_general.append([str(motivo), str(monto)])


    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe.pdf"+{socio.user.first_name}'
    doc = SimpleDocTemplate(response, pagesize=A4)

    elements = []

    title_style = ParagraphStyle(
        name='INFORME MENSUAL ADUTEQ',
        fontSize=14,
        alignment=TA_CENTER,
        spaceAfter=12,
        fontName='Helvetica-Bold',
    )

    title=Paragraph("Informe Mensual ADUTEQ", title_style)

    image_and_title = Table(
        [[img, title]],
        colWidths=[100, '*'], 
        style=[
            ('ALIGN', (0, 0), (0, 0), 'LEFT'), 
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),  
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
    )

    elements.append(image_and_title)
    elements.append(Spacer(1, 20))

    table_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), '#82F698'),  # Fondo verde pastel
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Texto blanco
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    data_tables = [
        ('Consumos por Proveedor', data),
        ('Consumos-de-Cuotas', data_cuotas),
        ('Aportaciones del Socio', data_aportaciones),
        ('Ayudas Económicas', data_ayuda),
        ('Tabla General', data_general)
    ]

    for title, data in data_tables:
        # Obtener el índice de la columna de montos en función del título de la tabla
        print(data_cuotas)
        monto_column_index = 1 if title != 'Consumos-de-Cuotas' else 3
        if title != 'Tabla General':
            # Verificar si al menos un monto en la tabla es diferente de 0 y no es nulo
            if any(row[monto_column_index] and row[monto_column_index] != 'None' and float(row[monto_column_index]) != 0 for row in data[monto_column_index:]):
                table_data = [[Paragraph(cell, ParagraphStyle('Normal')) for cell in row] for row in data]
                table = Table(table_data, colWidths='*')

                max_heights = []
                for row in table_data:
                    row_heights = []
                    for cell in row:
                        cell_paragraph = Paragraph(cell.getPlainText(), ParagraphStyle('Normal'))
                        avail_width, avail_height = cell_paragraph.wrapOn(doc, A4[0], A4[1])
                        cell_paragraph.wrap(avail_width, avail_height)
                        cell_height = cell_paragraph.height
                        row_heights.append(cell_height)
                    max_heights.append(max(row_heights))

                for row, max_height in zip(table_data, max_heights):
                    for cell in row:
                        cell._textValign = 'middle'
                        cell.height = max_height

                table.setStyle(table_style)
                elements.append(Paragraph(title, title_style))
                elements.append(Spacer(1, 12))
                elements.append(table)
                elements.append(Spacer(1, 20))
        else:
            elements.append(PageBreak())
            
            # Agregar el título de la tabla "Tabla General"
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 12))

            # Crear la tabla y aplicar estilos
            table_data = [[Paragraph(cell, ParagraphStyle('Normal')) for cell in row] for row in data]
            table = Table(table_data, colWidths='*')
            table.setStyle(table_style)

            # ... (ajustar alturas de celdas y aplicar estilos de tabla)

            # Agregar la tabla "Tabla General" a los elementos del PDF
            elements.append(table)
            elements.append(Spacer(1, 20))

    doc.build(elements)
    return response


##########################-------NUEVO ENVIAR CORREO------##############################

def nuevo_enviar_correo(request, socio_id):
    socio = Socios.objects.get(id=socio_id)
    hoy = datetime.today()

    numero_mes = hoy.month
    anio = hoy.year
    
    socio = Socios.objects.get(id=socio_id)
    resultados = obtener_datos_socioss(socio_id, numero_mes, anio)

    informe_data = enviar_datos_pdf(socio_id)

    if enviarGastoEmail(socio_id, resultados, informe_data):
        response = {'status': 'success', 'message': 'Promoción enviada a todos los socios'}
    else:
        response = {'status': 'error', 'message': 'Ups. algo salío mal'}

    return JsonResponse(response)



###################################---ENVIAR CORREO TODOS----############################
def enviar_correo_todos():
    socios=Socios.objects.all()
    hoy = datetime.today()
    for socio in socios:
        if(socio.user.is_active):
            try:
                numero_mes = hoy.month
                anio = hoy.year
                resultados = obtener_datos_socioss(socio.id, numero_mes, anio)
                informe_data = enviar_datos_pdf(socio.id)
                context={'gastos':resultados}

                template = get_template('gastosmensual.html')
                content = template.render(context)
                
                email = EmailMultiAlternatives(
                    'Informe mensual ADUTEQ',
                    'Gastos',
                    settings.EMAIL_HOST_USER,
                    [socio.user.email])
                email.attach_alternative(content, 'text/html')
                email.attach('informe.pdf', informe_data.getvalue(), 'application/pdf')
                email.send()
            except Exception as e:
                print(str(e))
    return True


def enviarGastoEmail(socio_id, context, pdf_buffer):
    sociop=Socios.objects.get(id=socio_id)
    gastos=context
    # correo=render_to_string('gastosmensual.html', {"gastos": gastos})
    context={'gastos':gastos}

    template =get_template('gastosmensual.html')
    content=template.render(context)
    email= EmailMultiAlternatives(
        'Informe mensual ADUTEQ',
        'Gastos',
        settings.EMAIL_HOST_USER,
        [sociop.user.email]
    )
    # email.attach_file("ADUTEQ\static\img\logo.png")
    email.attach_alternative(content, 'text/html')
    email.attach('informe.pdf', pdf_buffer.getvalue(), 'application/pdf')

    if sociop.user.is_active:
        email.send()
        return True
    else:
        return False
    

def enviar_correo_todoss(request):

    if enviar_correo_todos():
        response = {'status': 'success', 'message': 'Correo enviado a todos los socios'}
    else:
        response = {'status': 'error', 'message': 'Ups. algo salío mal'}

    return JsonResponse(response)

def reportes(request):
    return render(request, "reportes.html")

def obtener_consumo_total_func(mes, anio):
    
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT * FROM obtener_consumo_total_func({mes}, {anio});"
        )
        result = cursor.fetchall()
    return result

def generar_reporte_pdf_total_usuarios(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_consumo.pdf"'

    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    resultados = obtener_consumo_total_func(mes, anio)
    image_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'aduteq.png')
    total_consumo = obtener_suma_consumo_total_descuentos_func(mes, anio) or 0
    total_prestamo = obtener_suma_prestamo_total_func(mes, anio) or 0
    total_descuento_cuotas = obtener_suma_descuento_cuotas_func(mes, anio) or 0
    total_ayudas = obtener_suma_ayudas_func(mes, anio) or 0

    total = total_consumo + total_prestamo + total_descuento_cuotas + total_ayudas



    template = get_template('reporte_total_consu.html') 
    context = {'resultados': resultados,
               'mes': mes,
               'image_path': image_path,
                'anio': anio,
                'total': total
                } 

    html = template.render(context)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response.write(result.getvalue())
        return response

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
        prestamos_cuotas=obtener_cuota_prestamos_func(mes,anio)
        suma_prestamos=obtener_suma_prestamo_total_func(mes,anio)
        descuento_cuotas=obtener_cuota_descuentos_func(mes,anio)
        suma_des_cuot=obtener_suma_descuento_cuotas_func(mes,anio)
        ayudas_des=obtener_ayudas_func(mes,anio)
        suma_ayudas=obtener_suma_ayudas_func(mes,anio)
        return render(request, "cerrar_periodo.html", 
                      {'consumos_proveedores': consumos_proveedores, 'suma_consumo': suma_consumo,
                       'prestamos_cuotas': prestamos_cuotas, 'suma_prestamos': suma_prestamos,
                       'descuento_cuotas': descuento_cuotas, 'suma_des_cuot': suma_des_cuot,
                       'ayudas_des': ayudas_des, 'suma_ayudas': suma_ayudas})
    else:
        return render(request, 'login.html')
    
def obtener_consumos_proveedores_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM obtener_consumos_proveedores_func(%s, %s);", [mes, anio])
        results = cursor.fetchall()
    return results

def obtener_cuota_prestamos_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM obtener_cuota_prestamos_func(%s, %s);", [mes, anio])
        results = cursor.fetchall()
    return results

def obtener_cuota_descuentos_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM obtener_cuota_descuentos_func(%s, %s);", [mes, anio])
        results = cursor.fetchall()
    return results

def obtener_ayudas_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM obtener_ayudas_func(%s, %s);", [mes, anio])
        results = cursor.fetchall()
    return results

def actualizar_cancelados(request):
    checks=request.POST.getlist('socio_id[]')
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    with connection.cursor() as cursor:
        for id_socio in checks:
            cursor.execute("SELECT * FROM actualizar_cancelados(%s, %s, %s);", [mes, anio, id_socio])
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
    checks=request.POST.getlist('socio_id[]1')
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    with connection.cursor() as cursor:
        for id_socio in checks:
            cursor.execute("SELECT * FROM actualizar_estados(%s, %s, %s);", [mes, anio, id_socio])
    return redirect(cerrar_periodo)

def actualizar_descuentos(request):
    checks=request.POST.getlist('pago_id[]')
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    with connection.cursor() as cursor:
        for id_pago in checks:
            cursor.execute("SELECT * FROM actualizar_descuentos(%s, %s, %s);", [mes, anio, id_pago])
    return redirect(cerrar_periodo)
    
    
def obtener_suma_consumo_total_descuentos_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT obtener_suma_consumo_total_descuentos_func(%s, %s);", [mes, anio])
        suma_consumo = cursor.fetchone()[0]
    return suma_consumo

def obtener_suma_prestamo_total_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT obtener_suma_prestamo_total_func(%s, %s);", [mes, anio])
        suma_consumo = cursor.fetchone()[0]
    return suma_consumo

def obtener_suma_descuento_cuotas_func(mes, anio):
    with connection.cursor() as cursor:
        cursor.execute("SELECT obtener_suma_descuento_cuotas_func(%s, %s);", [mes, anio])
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
