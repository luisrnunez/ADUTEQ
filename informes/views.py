from django.shortcuts import redirect
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