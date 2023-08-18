from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Prestamo,Socios, PagoMensual
from django.contrib import messages
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger
from .models import Periodo
from django.template.loader import render_to_string

def guardar_prestamo(request):
    if request.method == 'POST':
        monto = request.POST.get('monto')
        fecha_prestamo = request.POST.get('fecha_prestamo')
        fecha_pago = request.POST.get('fecha_pago')
        plazo_meses = request.POST.get('plazo_meses')
        tasa_interes = request.POST.get('tasa_interes')
        descripcion = request.POST.get('descripcion')
        socio_id = request.POST.get('socio')
        socios = Socios.objects.get(id=socio_id)
        monto_total=float(monto)+((float(monto)*(float(tasa_interes)/100)))
        prestamo = Prestamo(socio=socios,monto=monto,fecha_pago=fecha_pago,fecha_prestamo=fecha_prestamo,total=monto_total, plazo_meses=plazo_meses, tasa_interes=tasa_interes, descripcion=descripcion)
        monto_pago_mensual=monto_total/float(plazo_meses)
        fecha_actual = datetime.now().date()
        # Calcular las fechas de pago para los próximos 8 meses

        fecha_actual_str = str(request.POST.get('fecha_prestamo'))
        fecha_actual = datetime.strptime(fecha_actual_str, "%Y-%m-%d")
        fechas_pago = [fecha_actual + timedelta(days=(30 * (i+1))) for i in range(int(plazo_meses))]

        if Prestamo.objects.filter(socio_id=socios, cancelado=False).exists():
            messages.warning(request,'Este socio ya tiene un prestamo activo por lo que no es posible registrar el prestamo')
            socios =  Socios.objects.select_related('user').all()
            return render(request, 'agregar_prestamo.html',{'socios' :socios,'prestamo' :prestamo})  
        
        prestamo.save()

        for numero_cuota, fecha_pago in enumerate(fechas_pago, start=1):
            pago_mensual = PagoMensual(
                socio=socios,
                prestamo=prestamo,
                numero_cuota=numero_cuota,
                monto_pago=monto_pago_mensual,
                cancelado=False,
                fecha_pago=fecha_pago
            )
            pago_mensual.save()

        messages.success(request,'EL prestamo fue creado exitosamente!!')

        return redirect('mostrar_prestamo')
    else:
        prestamo = Prestamo.objects.all()
        users = User.objects.filter(is_active=True)
        socios = Socios.objects.filter(user__in=users)
        
        return render(request, 'agregar_prestamo.html', {'prestamo': prestamo,'socios' : socios })



def editar_prestamo(request, prestamo_id):
    if request.method=='GET':
        prestamos = Prestamo.objects.get(id=prestamo_id)
        print(prestamo_id)
        socios =  Socios.objects.select_related('user').all()
        return render(request,'editar_prestamo.html', {'prestamo': prestamos,'socios' : socios })
    else:
        prestamos.prestamos = Prestamo.objects.get(id=prestamo_id)
        prestamos.monto = request.POST.get('monto')
        prestamos.fecha_prestamo = request.POST.get('fecha_prestamo')
        prestamos.fecha_pago = request.POST.get('fecha_pago')
        prestamos.plazo_meses = request.POST.get('plazo_meses')
        prestamos.tasa_interes = request.POST.get('tasa_interes')
        prestamos.descripcion = request.POST.get('descripcion')
        messages.success(request,'EL prestamo fue editado de forma exitosa')
        prestamos.save()

        return redirect('mostrar_prestamo')
    
def mostrar_prestamo(request):
    socios =  Socios.objects.select_related('user').all()

    periodos = Periodo.objects.all()  # Obtener todos los períodos
    anos = periodos.values_list('anio', flat=True).distinct()
    #listar periodo por el select
    periodoid = request.POST.get('periodoid')
    fechas_periodo = {}
    if periodoid:
        periodo_seleccionado = Periodo.objects.filter(id=periodoid).first()
        if periodo_seleccionado:
            fechas_periodo = {
                'fecha_inicio': periodo_seleccionado.fecha_inicio,
                'fecha_fin': periodo_seleccionado.fecha_fin
            }
            prestamos = Prestamo.objects.filter(fecha_prestamo__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])).order_by("-fecha_prestamo", "socio")
            context = {
                'prestamos': prestamos,
                'socios' : socios ,
                'periodos': periodos,
                'anos': anos,
                'fechas_periodo': fechas_periodo,
                'periodo_seleccionado': periodo_seleccionado,
            }
            rendered_table = render_to_string("mostrar_prestamo_partial.html",context)
            return JsonResponse({"rendered_table": rendered_table})
    
    #listar periodo actual
    periodo_seleccionado = Periodo.objects.filter(activo=True).first()
    if periodo_seleccionado:
        fechas_periodo = {
            'fecha_inicio': periodo_seleccionado.fecha_inicio,
            'fecha_fin': periodo_seleccionado.fecha_fin
        }
        prestamos = Prestamo.objects.filter(fecha_prestamo__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])).order_by("-fecha_prestamo", "socio")
        items_por_pagina = 8
        paginator = Paginator(prestamos, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            prestamos = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            prestamos = paginator.get_page(1)
    else:
        prestamos = {}
    context = {
                'prestamos': prestamos,
                'socios' : socios ,
                'periodos': periodos,
                'anos': anos,
                'fechas_periodo': fechas_periodo,
                'periodo_seleccionado': periodo_seleccionado,
            }
    return render(request, 'mostrar_prestamo.html', context)



    # prestamos = Prestamo.objects.all().order_by('cancelado')
    # items_por_pagina = 8
    # paginator = Paginator(prestamos, items_por_pagina)
    # numero_pagina = request.GET.get('page')
    # try:
    #     prestamos_paginados = paginator.get_page(numero_pagina)
    # except PageNotAnInteger:
    #     prestamos_paginados = paginator.get_page(1)
    # socios =  Socios.objects.select_related('user').all()
    # return render(request, 'mostrar_prestamo.html', {'prestamos': prestamos_paginados,'socios' : socios })


def aplicar_pago(request, prestamo_id, valor):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)

    if request.method == 'GET':
        # Cambiar el estado del socio a inactivo
        print (valor)
        if valor == 0:
            prestamo.cancelado = True
            prestamo.fecha_pago = date.today()
            prestamo.save()
            messages.success(
            request, 'Se ha registrado el pago del prestamo exitosamente.')
        #else:
            #pagosproveedor.activo = False
            #pagosproveedor.save()
            #messages.success(
            #request, 'El socio ha sido dado de baja exitosamente.')

        # Agregar un mensaje de confirmación

    else:
        messages.warning(request, 'El pago no pudo ser procesado')

    return redirect('mostrar_prestamo')




#-----------------------------------------Cuotas------------------------------------#
def guardar_pago_cuota(request):
    if request.method == 'POST':
        socio_id = request.POST.get('socio')
        prestamo_id = request.POST.get('prestamo')
        monto = request.POST.get('monto')
        numero_cuota = request.POST.get('num_cuota')
        evidencia= request.POST.get('evidencia')
        fecha_pago= request.POST.get('fecha_pago')
        socios = Socios.objects.get(id=socio_id)
        pres=Prestamo.objects.get(id=prestamo_id)
        #pagoMensual = PagoMensual(socio=socios,prestamo=pres ,numero_cuota=numero_cuota,monto_pago=monto,evidencia=evidencia,fecha_pago=fecha_pago)
        if Prestamo.objects.filter(socio_id=socios, cancelado=False).exists():
            #messages.warning(request,'Este socio ya tiene un prestamo activo por lo que no es posible registrar el prestamo')
            socios =  Socios.objects.select_related('user').all()
            PagoMensual.objects.create(socio=socios, prestamo=pres ,numero_cuota=numero_cuota, monto_pago=monto, evidencia=evidencia, fecha_pago=fecha_pago)
            prestamoss=Prestamo.objects.all();
            messages.warning(request,'Pago registrado correctamente')
            return render(request, 'agregar_cuota.html',{'socios' :socios,'prestamo' :prestamoss})  
        
        # messages.success(request,'EL prestamo fue creado exitosamente!!')
        # Prestamo.objects.create(socio=socios,monto=monto,fecha_pago=fecha_pago,fecha_prestamo=fecha_prestamo, plazo_meses=plazo_meses, tasa_interes=tasa_interes, descripcion=descripcion,cancelado=False)

        return redirect('mostrar_detalles_pago')
    else:
        prestamo = Prestamo.objects.all()
        users = User.objects.filter(is_active=True)
        socios = Socios.objects.filter(user__in=users)
        
        return render(request, 'agregar_prestamo.html', {'prestamo': prestamo,'socios' : socios })
    

def mostrar_detalles(request, socio_id, prestamo_id):
    soci=Socios.objects.get(id=socio_id)
    prestamo=Prestamo.objects.get(id=prestamo_id)
    pagoMensual = PagoMensual.objects.filter(socio=soci, prestamo=prestamo).order_by('cancelado','numero_cuota')
    items_por_pagina = 8
    paginator = Paginator(pagoMensual, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        prestamos_paginados = paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        prestamos_paginados = paginator.get_page(1)
    #print(pagoMensual)
    socios =  Socios.objects.select_related('user').all()
    return render(request, 'mostrar_detalles_prestamo.html', {'cuotas': prestamos_paginados,'socio' : soci })


def mostrar_detalles_todo(request):
    pagoMensual = PagoMensual.objects.all().order_by("fecha_pago")
    #print(pagoMensual)
    socios =  Socios.objects.select_related('user').all()
    return render(request, 'mostrar_detalles_prestamo.html', {'cuotas': pagoMensual,'socios' : socios })

def aplicar_pago_cuota(request, cuota_id, valor, socio_id, prestamo_id):
    prestamo=Prestamo.objects.get(id=prestamo_id)
    socio=Socios.objects.get(id=socio_id)
    #cuota actual
    cuota = get_object_or_404(PagoMensual, id=cuota_id, socio=socio, prestamo=prestamo)
    #todas las cuotas del prestamo
    cuotas=PagoMensual.objects.filter(prestamo=prestamo)
    #ordenas las cuotas
    cuotas_ord=PagoMensual.objects.filter(prestamo=prestamo).order_by('fecha_pago')
    #ultima cuota
    ult_cuota=cuotas.last()
    #cuota anterior a la actual
    cuota_anterior = cuotas_ord.filter(fecha_pago__lt=cuota.fecha_pago).last()
    # print(cuota)
    # print(cuota_anterior)
    if request.method == 'GET':
        # Cambiar el estado del cancelado
        print (valor)
        if cuota_anterior is not None and not cuota_anterior.cancelado:
            messages.warning(request, "Una o varias de las cuotas anteriores no se encuentran canceladas")
            
        else:
            if valor == 0:
                cuota.cancelado = True
                #cuota.fecha_pago = date.today()
                cuota.save()
                messages.success(
                request, 'Se ha registrado el pago de la cuota exitosamente.')
                if cuota==ult_cuota:
                    messages.success(request, 'Prestamo de '+ socio.user.first_name +' cancelado completamente')
                    return redirect('mostrar_prestamo')
            #else:
            #pagosproveedor.activo = False
            #pagosproveedor.save()
            #messages.success(
            #request, 'El socio ha sido dado de baja exitosamente.')

            # Agregar un mensaje de confirmación

    else:
        messages.warning(request, 'El pago no pudo ser procesado')
    return redirect('/detalles_pago/'+ str(socio_id) +'/'+str(prestamo_id))

def editar_detalles(request, detalle_id, socio_id, prestamo_id):
    if request.method=='GET':
        pagoMensual = PagoMensual.objects.get(id=detalle_id)
        print(detalle_id)
        socios =  Socios.objects.select_related('user').all()
        return render(request,'editar_detalles_prestamo.html', {'prestamo': pagoMensual,'socios' : socios })
    else:
        # socio=pagoMensual.socio
        # prestamo=pagoMensual.prestamo
        # numcuota=pagoMensual.numero_cuota
        # monto=pagoMensual.monto_pago
        # evidencia=pagoMensual.evidencia
        # cancela=pagoMensual.cancelado
        # fechap=pagoMensual.fecga_pago

        pagoMensual.evidencia=request.FILES['evidencia']
        messages.success(request,'EL prestamo fue editado de forma exitosa')
        pagoMensual.save()

        return redirect('/detalles_pago/'+ str(socio_id) +'/'+str(prestamo_id))
    
def presagregar_pdf(request, det_id): 
    pago_men = PagoMensual.objects.get(id=det_id)
    if request.method == 'GET':
        return render(request,'editar_detalles_prestamo.html', {'pago_men': pago_men}) 
    else:
        archivo_pdf = request.FILES['evidencia']
        pago_men.evidencia=archivo_pdf
        pago_men.save()
        return redirect('/detalles_pago/' + str(pago_men.socio.id) +'/'+ str(pago_men.prestamo.id))


#eliminar prestamos y sus respectivas cuotas
def eliminar_prestamo_y_cuotas(request, prestamo_id):
    try:
        with transaction.atomic():

            pago = get_object_or_404(Prestamo, id=prestamo_id)
            cuotas_canceladas = PagoMensual.objects.filter(prestamo=pago, cancelado=True)
            if cuotas_canceladas.exists():
                messages.warning(request, 'No se puede eliminar el descuento. Hay cuotas canceladas asociadas a este pago.')
                return redirect('mostrar_prestamo')

            # Obtenemos el préstamo
            prestamo = Prestamo.objects.get(id=prestamo_id)

            # Eliminamos todas las cuotas del préstamo
            PagoMensual.objects.filter(prestamo=prestamo).delete()

            # Eliminamos el préstamo
            prestamo.delete()
            messages.success(request,'EL prestamo fue eliminado de manera exitosa!!')

    except Exception as e:
        # Si ocurre algún error durante la transacción, la transacción se revierte automáticamente
        messages.warning(request,'Ups, ha ocurrido un problema')
    return redirect('mostrar_prestamo')