from django.shortcuts import redirect, render
from Pagos.models import Pagos
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from socios.models import Socios
from proveedores.models import Proveedor
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from datetime import datetime, timedelta
from django.db.models import Sum


# Create your views here.

def obtenerValores(socio_id):
    sociop=Socios.objects.get(id=socio_id)

    #obtener consumos totales de un socio
    hoy = datetime.today()
    ultimo_mes = hoy - timedelta(days=30)
    total_general = 0
    gastos_por_proveedor = Pagos.objects.filter(socio_id=socio_id, fecha_consumo__gte=ultimo_mes).values('proveedor').annotate(total_proveedor=Sum('consumo_total'))
    gastos_por_proveedor_list = []
    for gasto_proveedor in gastos_por_proveedor:
        proveedor = gasto_proveedor['proveedor']
        total_proveedor = gasto_proveedor['total_proveedor']
        nameproveedor=Proveedor.objects.get(id=proveedor)
        total_general +=total_proveedor
        gastos_por_proveedor_list.append({'proveedor': nameproveedor.nombre, 'total_proveedor': total_proveedor, 'total':total_general})
    

    print(gastos_por_proveedor, total_general)
    return gastos_por_proveedor_list

def enviarGastoEmail(socio_id):
    sociop=Socios.objects.get(id=socio_id)
    gastos=obtenerValores(socio_id)
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

    if sociop.user.is_active:
        email.send()
        return True
    else:
        return False



def enviar_correo(request, socio_id):

    if enviarGastoEmail(socio_id):
        messages.success(request, 'El correo se envió correctamente.')
    else:
        messages.info(request, 'El socio no se encuentra activo actualmente.')

    return redirect('/socios')

# def enviar_correo(request, socio_id):

#     if enviarGastoEmail(socio_id):
#         response = {
#                 'status': 'success',
#                 'message': 'Correo enviado crrectamente'
#             }
#         # messages.success(request, 'El correo se envió correctamente.')
#     else:
#         response = {
#                 'status': 'error',
#                 'message': 'Ha ocurriod un error'
#             }
#         # messages.error(request, 'Hubo un error al enviar el correo.')

#     return JsonResponse(response)


#---------------------------------------enviar correo a todos-------------------

def enviarGastoEmailTodos():
    sociop=Socios.objects.all()
    for socio in sociop:
        if socio.user.is_active:
            try:
                gastos=Pagos.objects.filter(socio=socio)
                print(gastos)
                # correo=render_to_string('gastosmensual.html', {"gastos": gastos})

                context={'gastos':gastos}
                template =get_template('gastosmensual.html')
                content=template.render(context)
                email= EmailMultiAlternatives(
                    'Informe mensual ADUTEQ',
                    'Gastos',
                    settings.EMAIL_HOST_USER,
                    [socio.user.email]
                )
                email.attach_alternative(content, 'text/html')

                email.send()

            except Exception as e:
                print(str(e))
                return False
    return True

def enviar_correo_todos(request):

    if enviarGastoEmailTodos():
        messages.success(request, 'Correos enviados correctamente.')
    else:
        messages.info(request, 'Ups, ah ocurrido un error.')

    return redirect('/socios')
        # gastos=obtenerValores()
        # correo=render_to_string('gastosmensual.html', {"gastos": gastos})


        # try:
        #     send_mail(
        #         'Informe mensual ADUTEQ',
        #         correo,
        #         'email',
        #         [socio.correo_electronico],
        #         fail_silently=False
        #     )
        #     return True
        # except Exception as e:
        #     print(str(e))
        #     return False