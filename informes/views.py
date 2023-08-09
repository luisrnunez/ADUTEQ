from django.shortcuts import redirect,render
from Pagos.models import Pagos
from django.contrib import messages
from socios.models import Socios, Aportaciones
from proveedores.models import Proveedor
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from ayudas_econ.models import DetallesAyuda
from Pagos.models import Pagos_cuotas, Detalle_cuotas
from datetime import datetime, timedelta
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.contrib.auth.models import User
from django.db import connection
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Image,Spacer


# Create your views here.

def obtener_gastos_socio(socio_id):
    # Obtener el socio específico
    socio = Socios.objects.get(id=socio_id)

    # obtener la fecha del primer dia del mes actual
    hoy = datetime.today()
    primer_dia_mes_actual = hoy - timedelta(days=30)

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

    print(total_total)
    return gastos_por_proveedor, gastos_por_proveedor_cuotas, aportaciones_socio, ayuda,total_gastos_proveedor,total_gastos_proveedor_cuotas,total_aportaciones_socio, total_ayuda, total_total

def enviar_correo_uno(request,socio_id):
    socio = Socios.objects.get(id=socio_id)
    gastos_por_proveedor, gastos_por_proveedor_cuotas, aportaciones_socio, ayuda, total_gastos_proveedor,total_gastos_proveedor_cuotas,total_aportaciones_socio, total_ayuda, total_total = obtener_gastos_socio(socio_id)

    context = {
        'socio': socio,
        'gastos_por_proveedor': gastos_por_proveedor,
        'total_pagos_cuotas': gastos_por_proveedor_cuotas,
        'aportaciones_socio': aportaciones_socio,
        'ayudasEcon_socio': ayuda,

        'total_gastos_proveedor': total_gastos_proveedor,
        'total_gastos_proveedor_cuotas': total_gastos_proveedor_cuotas,
        'total_aportaciones_socio': total_aportaciones_socio,
        'total_ayuda': total_ayuda,
        'total_total': total_total,
    }


    if enviarGastoEmail(socio_id, context):
        messages.success(request, 'El correo se envió correctamente.')
    else:
        messages.info(request, 'El socio no se encuentra activo actualmente.')

    return redirect('/socios')

###################################---ENVIAR CORREO TODOS----############################
def enviar_correo_todos():
    socios=Socios.objects.all()
    
    for socio in socios:
        if(socio.user.is_active):
            try:
                gastos_por_proveedor, gastos_por_proveedor_cuotas, aportaciones_socio, ayuda, total_gastos_proveedor,total_gastos_proveedor_cuotas,total_aportaciones_socio, total_ayuda, total_total = obtener_gastos_socio(socio.id)

                context = {
                    'socio': socio,
                    'gastos_por_proveedor': gastos_por_proveedor,
                    'total_pagos_cuotas': gastos_por_proveedor_cuotas,
                    'aportaciones_socio': aportaciones_socio,
                    'ayudasEcon_socio': ayuda,

                    'total_gastos_proveedor': total_gastos_proveedor,
                    'total_gastos_proveedor_cuotas': total_gastos_proveedor_cuotas,
                    'total_aportaciones_socio': total_aportaciones_socio,
                    'total_ayuda': total_ayuda,
                    'total_total': total_total,
                }
                template = get_template('gastosmensual.html')
                content = template.render(context)
                
                email = EmailMultiAlternatives(
                    'Informe mensual ADUTEQ',
                    'Gastos',
                    settings.EMAIL_HOST_USER,
                    [socio.user.email])
                email.attach_alternative(content, 'text/html')
                email.send()
            except Exception as e:
                print(str(e))
    return True


def enviarGastoEmail(socio_id, context):
    sociop=Socios.objects.get(id=socio_id)
    gastos=context
    # correo=render_to_string('gastosmensual.html', {"gastos": gastos})
    context={'gastos':gastos}

    template =get_template('gastosmensual.html')
    content=template.render(gastos)
    email= EmailMultiAlternatives(
        'Informe mensual ADUTEQ',
        'Gastos',
        settings.EMAIL_HOST_USER,
        [sociop.user.email]
    )
    # email.attach_file("ADUTEQ\static\img\logo.png")
    email.attach_alternative(content, 'text/html')

    if sociop.user.is_active:
        email.send()
        return True
    else:
        return False
    

def enviar_correo_todoss(request):

    if enviar_correo_todos():
        messages.success(request, 'Correos enviados correctamente.')
    else:
        messages.info(request, 'Ups, ah ocurrido un error.')

    return redirect('/socios')

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

    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    elements = []

    imagen = cargar_imagen('informes/static/img/aduteq.png')  # Ruta relativa desde la ubicación de la función
    elements.append(imagen)


    data = [['Nombre', 'Cédula', 'Cuota de préstamos', 'Aportación', 'Descuento de proveedores', 'Aportación Ayudas', 'Consumo total']]
    data.extend(resultados)

    table = Table(data, colWidths=[130, 100, 100, 100, 140, 100, 100], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0x62/255, 0xc5/255, 0x62/255)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
    ]))

    elements.append(Spacer(1, 20))
    elements.append(table)
    doc.build(elements)
    return response

def cargar_imagen(path):
    imagen = Image(path)
    imagen.drawHeight = 50  # Ajusta la altura de la imagen
    imagen.drawWidth = 50   # Ajusta el ancho de la imagen
    return imagen