import datetime
from decimal import Decimal, ROUND_HALF_UP
from gettext import translation
from ipaddress import summarize_address_range
import os
import re
import PyPDF2
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Socios, Proveedor, Pagos, Pagos_cuotas, Detalle_cuotas, pagos_pendientes,detalle_cuotas_pendientes,pagos_cuotas_pendientes
from proveedores.models import detallesCupos
from .forms import PagosForm
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timedelta
import tabula
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger
from django.db import connection
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, KeepInFrame, Image
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.auth.decorators import login_required
from Periodo.models import Periodo
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf.default import DEFAULT_FONT
from reportlab.lib.units import inch
from .models import PagosProveedor
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.views.decorators.cache import cache_control


# Create your views here. 

@login_required
def principal_resumen(request):

    periodo = Periodo.objects.filter(activo=True).first()

  
    data = []
    year = datetime.now().year
    mes = datetime.now().month
    for month in range(1, 13):
        # Filtrar descuentos normales por año y mes
        descuentos_normales = Pagos.objects.filter(
            fecha_consumo__year=year, fecha_consumo__month=month
        )

        # Filtrar descuentos por cuotas por año y mes
        descuentos_cuotas = Pagos_cuotas.objects.filter(
            fecha_descuento__year=year, fecha_descuento__month=month
        )

        # Sumar los valores de consumo en descuentos normales
        total_normales = sum(float(descuento.consumo_total) if descuento.consumo_total is not None else 0 for descuento in descuentos_normales)

        # Sumar los valores de consumo en descuentos por cuotas
        total_cuotas = sum(float(descuento.consumo_total) if descuento.consumo_total is not None else 0 for descuento in descuentos_cuotas)

        # Calcular la suma total por mes
        suma_total = total_normales + total_cuotas
        if mes == month:
            suma_consumos = round(suma_total, 2)
        if mes > 1:
            if (mes-1) == month:
                suma_consumos_mesante = round(suma_total, 2)
        if mes == 1:
            if (12) == month:
                suma_consumos_mesante = round(suma_total, 2)

        # Agregar el resultado al array data
        data.append(suma_total)

    # MOSTRAR GANANCIAS
    comision = PagosProveedor.objects.filter(
            fecha_creacion__year=year, fecha_creacion__month=mes
        )
    total_comision = sum(float(suma.comision) if suma.comision is not None else 0 for suma in comision)

    #MOSTRAR GANANCIAS PASADAS
    if mes == 1:
        mes == 12
    else: mes = mes - 1
    comision = PagosProveedor.objects.filter(
            fecha_creacion__year=year, fecha_creacion__month = mes
        )
    total_comision_mesantes = sum(float(suma.comision) if suma.comision is not None else 0 for suma in comision)


    # MOSTRAR SUMA TOTAL DE SOCIOS
    socios = Socios.objects.all()
    total_socios = len(socios)
    socios = User.objects.filter(is_active=False,is_staff=False,is_superuser=False)
    total_socios_inactivos = len(socios) if socios is not None else 0 

     # MOSTRAR SUMA TOTAL DE PROVEEDOR
    prov = Proveedor.objects.all()
    total_prov = len(prov)
    prov = Proveedor.objects.filter(estado=False)
    total_prov_inactivo = len(prov) if prov is not None else 0 
  # MOSTRAR SUMA TOTAL DE COMISION DEL MES ACTUAL

    
    
    data2 = {}
    data2.update({
        'total_comision':total_comision,
        'total_socios':total_socios,
        'total_prov':total_prov,
        'suma_consumos':suma_consumos,
        'total_socios_inactivos':total_socios_inactivos,
        'total_prov_inactivo':total_prov_inactivo,
        'suma_consumos_mesante':suma_consumos_mesante,
        'total_comision_mesantes':total_comision_mesantes,
    })

    
    return render(request,'principal.html',{'periodo':periodo,'data':data,'data2':data2})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_pagos(request):

    periodos = Periodo.objects.all()  # Obtener todos los períodos
    anos = periodos.values_list('anio', flat=True).distinct()
    #listar periodo por el select
    periodoid = request.POST.get('periodoid')
    fechas_periodo = {}
    if periodoid:
        periodo_seleccionado = Periodo.objects.filter(id=periodoid).first()
        print(periodo_seleccionado)
        if periodo_seleccionado:
            fechas_periodo = {
                'fecha_inicio': periodo_seleccionado.fecha_inicio,
                'fecha_fin': periodo_seleccionado.fecha_fin
            }
           
            print(periodo_seleccionado)
            pagos = Pagos.objects.filter(fecha_consumo__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])).order_by("-id","socio","proveedor")
            context = {
                'pagos': pagos,
                'periodos': periodos,
                'anos': anos,
                'fechas_periodo': fechas_periodo,
                'periodo_seleccionado': periodo_seleccionado,
            }
            rendered_table = render_to_string("lista_pagos_partial.html",context)
            return JsonResponse({"rendered_table": rendered_table})
    
    #listar periodo actual
    periodo_seleccionado = Periodo.objects.filter(activo=True).first()
    if periodo_seleccionado:
        fechas_periodo = {
            'fecha_inicio': periodo_seleccionado.fecha_inicio,
            'fecha_fin': periodo_seleccionado.fecha_fin
        }
        pagos = Pagos.objects.filter(fecha_consumo__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])).order_by("-id","-fecha_consumo", "proveedor")
        items_por_pagina = 20
        paginator = Paginator(pagos, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            pagos = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            pagos = paginator.get_page(1)
    else:
        pagos = {}
    context = {
        'pagos': pagos,
        'periodos': periodos,
        'anos': anos,
        'fechas_periodo': fechas_periodo,
        'periodo_seleccionado': periodo_seleccionado,
    }
    return render(request, 'listar_pagos.html', context)

def listar_pagos_pendientes(request):

    periodos = Periodo.objects.all() 
    anos = periodos.values_list('anio', flat=True).distinct()
    #listar periodo por el select
    periodoid = request.POST.get('periodoid')
    fechas_periodo = {}
    if periodoid:
        periodo_seleccionado = Periodo.objects.filter(id=periodoid).first()
        print(periodo_seleccionado)
        if periodo_seleccionado:
            fechas_periodo = {
                'fecha_inicio': periodo_seleccionado.fecha_inicio,
                'fecha_fin': periodo_seleccionado.fecha_fin
            }
           
            print(periodo_seleccionado)
            pagos = pagos_pendientes.objects.filter(fecha_consumo__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin']))
            context = {
                'pagos': pagos,
                'periodos': periodos,
                'anos': anos,
                'fechas_periodo': fechas_periodo,
                'periodo_seleccionado': periodo_seleccionado,
            }
            rendered_table = render_to_string("list_pag_pen_par.html",context)
            return JsonResponse({"rendered_table": rendered_table})
    
    #listar periodo actual
    periodo_seleccionado = Periodo.objects.filter(activo=True).first()
    if periodo_seleccionado:
        fechas_periodo = {
            'fecha_inicio': periodo_seleccionado.fecha_inicio,
            'fecha_fin': periodo_seleccionado.fecha_fin
        }
        pagos = pagos_pendientes.objects.filter(fecha_consumo__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin']))
        items_por_pagina = 20
        paginator = Paginator(pagos, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            pagos = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            pagos = paginator.get_page(1)
    else:
        pagos = {}
    context = {
        'pagos': pagos,
        'periodos': periodos,
        'anos': anos,
        'fechas_periodo': fechas_periodo,
        'periodo_seleccionado': periodo_seleccionado,
    }
    return render(request, 'listar_pagos_pendientes.html', context)

def obtener_periodos_por_anio(request, anio):
    periodos = Periodo.objects.filter(anio=anio).values('id', 'nombre')
    return JsonResponse({'periodos': list(periodos)})


from django.db.models import Q
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_pagos_cuotas(request):
    periodos = Periodo.objects.all()  # Obtener todos los períodos
    anos = periodos.values_list('anio', flat=True).distinct()
    #listar periodo por el select
    periodoid = request.POST.get('periodoid')
    fechas_periodo = {}
    if periodoid:
        periodo_seleccionado = Periodo.objects.filter(id=periodoid).first()
        print(periodo_seleccionado)
        if periodo_seleccionado:
            fechas_periodo = {
                'fecha_inicio': periodo_seleccionado.fecha_inicio,
                'fecha_fin': periodo_seleccionado.fecha_fin
            }
           
            print(periodo_seleccionado)
            pagos = Pagos_cuotas.objects.filter(
                Q(fecha_descuento__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])) |
                Q(fecha_descuento__lt=fechas_periodo['fecha_inicio'], estado="False")
            ).order_by("-id","estado")
    
            context = {
                'pago_cuotas': pagos,
                'periodos': periodos,
                'anos': anos,
                'fechas_periodo': fechas_periodo,
                'periodo_seleccionado': periodo_seleccionado,
            }
            rendered_table = render_to_string("pagos_cuotas_partial.html",context)
            return JsonResponse({"rendered_table": rendered_table})
    
    #listar periodo actual
    periodo_seleccionado = Periodo.objects.filter(activo=True).first()
    if periodo_seleccionado:
        fechas_periodo = {
            'fecha_inicio': periodo_seleccionado.fecha_inicio,
            'fecha_fin': periodo_seleccionado.fecha_fin
        }
        pagos = Pagos_cuotas.objects.filter(
                Q(fecha_descuento__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])) |
                Q(fecha_descuento__lt=fechas_periodo['fecha_inicio'], estado="False")
            ).order_by("-id","estado")
        items_por_pagina = 10
        paginator = Paginator(pagos, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            pagos = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            pagos = paginator.get_page(1)
    else:
        pagos = {}
    context = {
        'pago_cuotas': pagos,
        'periodos': periodos,
        'anos': anos,
        'fechas_periodo': fechas_periodo,
        'periodo_seleccionado': periodo_seleccionado,
    }
    return render(request, 'pagos_cuotas.html', context)


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def extraer_descuentos(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'extraer_descuentos.html', {'proveedores': proveedores})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def agrefar_pagos(request):
    if request.method == 'GET':
        users = User.objects.filter(is_active=True)
        socios = Socios.objects.filter(user__in=users)
        proveedores = Proveedor.objects.filter(estado=True)
        return render(request, 'agregar_pago.html', {'socios': socios, 'proveedores': proveedores})
    else:
        socio_id = request.POST.get('socio')
        socios = Socios.objects.get(id=socio_id)
        proveedor_id = request.POST.get('proveedor')
        proveedores = Proveedor.objects.get(id=proveedor_id)
        cupo=detallesCupos.objects.get(proveedor=proveedores,socio=socios)
        fecha = request.POST.get('fecha_consumo')
        cantidad = request.POST.get('consumo_total')

        periodo_seleccionado = Periodo.objects.filter(activo=True).first()
        if periodo_seleccionado and periodo_seleccionado.fecha_inicio <= datetime.strptime(fecha, '%Y-%m-%d').date() <= periodo_seleccionado.fecha_fin:
            if(float(cantidad)<=cupo.cupo):
                pagos = Pagos.objects.create(socio=socios, proveedor=proveedores, consumo_total=cantidad, fecha_consumo=fecha)
                messages.success(request, 'Exito')
                return redirect('/listar_pagos/')
            else:
                messages.warning(request, 'La cantidad que desea ingresar es superior a la brindada por el proveedor')
            return redirect('/listar_pagos/')
        else:
            messages.warning(request, f'La fecha que ingresaste no esta dentro del periodo actual de {periodo_seleccionado.nombre}')
            users = User.objects.filter(is_active=True)
            socios = Socios.objects.filter(user__in=users)
            proveedores = Proveedor.objects.filter(estado=True)
            return render(request, 'agregar_pago.html', {'socios': socios, 'proveedores': proveedores})
        

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def agregar_pagos_pendiente(request):
    if request.method == 'GET':
        users = User.objects.filter(is_active=True)
        socios = Socios.objects.filter(user__in=users)
        return render(request, 'agregar_pago_pendiente.html', {'socios': socios})
    else:
        socio_id = request.POST.get('socio')
        socios = Socios.objects.get(id=socio_id)
        fecha = request.POST.get('fecha_consumo')
        cantidad = request.POST.get('consumo_total')

        periodo_seleccionado = Periodo.objects.filter(activo=True).first()
        if periodo_seleccionado and periodo_seleccionado.fecha_inicio <= datetime.strptime(fecha, '%Y-%m-%d').date() <= periodo_seleccionado.fecha_fin:
            if(float(cantidad)<=10000):
                pagos = pagos_pendientes.objects.create(socio=socios, consumo_total=cantidad, fecha_consumo=fecha)
                messages.success(request, 'Exito')
                return redirect('/listar_pagos_pendientes/')
            else:
                messages.warning(request, 'La cantidad que desea ingresar es superior a la brindada por el proveedor')
            return redirect('/listar_pagos_pendientes/')
        else:
            messages.warning(request, f'La fecha que ingresaste no esta dentro del periodo actual de {periodo_seleccionado.nombre}')
            users = User.objects.filter(is_active=True)
            socios = Socios.objects.filter(user__in=users)
            proveedores = Proveedor.objects.filter(estado=True)
            return render(request, 'agregar_pago_pendiente.html', {'socios': socios, 'proveedores': proveedores})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def agregar_pagos_cuotas(request):
    try:
        with transaction.atomic():
            if request.method == 'GET':
                users = User.objects.filter(is_active=True)
                socios = Socios.objects.filter(user__in=users)
                proveedores = Proveedor.objects.filter(estado=True)
                return render(request, 'agregar_pago_cuotas.html', {'socios': socios, 'proveedores': proveedores})
            else:
                socio_id = request.POST.get('socio')
                socios = Socios.objects.get(id=socio_id)

                proveedor_id = request.POST.get('proveedor')
                proveedores = Proveedor.objects.get(id=proveedor_id)

                cantidad = request.POST.get('consumo_total')
                numero_cuota = request.POST.get('numero_cuotas')

                fecha_descuento = str(request.POST.get('fecha_descuento'))
                fecha_actual = datetime.strptime(fecha_descuento, "%Y-%m-%d")
                
                if fecha_actual.day < 15:
                    fecha_inicio_pagos = fecha_actual.replace(day=15)
                else:
                    next_month = fecha_actual.replace(day=1) + timedelta(days=32)
                    fecha_inicio_pagos = next_month.replace(day=15)
                
                cantidadval = float(cantidad)
                n_cuota = float(numero_cuota)
                valor_cuo = cantidadval / n_cuota

                periodo_seleccionado = Periodo.objects.filter(activo=True).first()
                if periodo_seleccionado and periodo_seleccionado.fecha_inicio <= datetime.strptime(fecha_descuento, '%Y-%m-%d').date() <= periodo_seleccionado.fecha_fin:
                    pagoscuotas = Pagos_cuotas.objects.create(
                        socio=socios, proveedor=proveedores, consumo_total=cantidad, fecha_descuento=fecha_descuento,
                        numero_cuotas=numero_cuota, cuota_actual=0, valor_cuota=valor_cuo
                    )
                    pagoscuotas.save()

                    fechas_pago = [fecha_inicio_pagos + timedelta(days=(30 * i)) for i in range(int(numero_cuota))]
                    
                    for numero_cuota, fecha_pago in enumerate(fechas_pago, start=1):
                        detalle_cuotas = Detalle_cuotas(
                            pago_cuota=pagoscuotas,
                            numero_cuota=numero_cuota,
                            fecha_descuento=fecha_pago,
                            valor_cuota=valor_cuo,
                            socio=socios, proveedor=proveedores
                        )
                        detalle_cuotas.save()

                    messages.success(request, 'Se ha agregado con éxito el descuento por cuotas')
                    return redirect('/lista_pagos_cuotas/')
                else:
                    messages.warning(request, f'La fecha que ingresaste no está dentro del período actual de {periodo_seleccionado.nombre}')
                    users = User.objects.filter(is_active=True)
                    socios = Socios.objects.filter(user__in=users)
                    proveedores = Proveedor.objects.filter(estado=True)
                    return render(request, 'agregar_pago_cuotas.html', {'socios': socios, 'proveedores': proveedores})
            
    except Exception as e:
        messages.warning(request, 'Ups, ha ocurrido un problema, verifica los valores ingresados')
    return redirect('/lista_pagos_cuotas/')



@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editar_pago(request, pago_id):
    if request.method == 'GET':
        pagos = Pagos.objects.get(id=pago_id)
        form = PagosForm(instance=pagos)
        return render(request, 'editar_pago.html', {'pagos': pagos, 'form': form})
    else:
        pagos = Pagos.objects.get(id=pago_id)
        pagos.consumo_total = request.POST.get('consumo_total')
        pagos.fecha_consumo = request.POST.get('fecha_consumo')
        pagos.estado=request.POST.get('estado')
        pagos.save()
        return redirect('/listar_pagos/')
    
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def editar_pago_pendiente(request, pago_id):
    if request.method == 'GET':
        pagos = pagos_pendientes.objects.get(id=pago_id)
        form = PagosForm(instance=pagos)
        return render(request, 'editar_pago_pendiente.html', {'pagos': pagos, 'form': form})
    else:
        pagos = pagos_pendientes.objects.get(id=pago_id)
        pagos.consumo_total = request.POST.get('consumo_total')
        pagos.fecha_consumo = request.POST.get('fecha_consumo')
        pagos.estado=request.POST.get('estado')
        pagos.save()
        messages.success(request, 'Se ha editado el descuento exitosamente.')
        return redirect('/listar_pagos_pendientes/')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detalles_cuota(request, pago_cuota_id):
    detalle_cuotas = Detalle_cuotas.objects.filter(pago_cuota=pago_cuota_id).order_by("estado", "numero_cuota")
    pago_cu = Pagos_cuotas.objects.get(id=pago_cuota_id)
    items_por_pagina = 8
    paginator = Paginator(detalle_cuotas, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        detalles_paginados=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        detalles_paginados=paginator.get_page(1)
    return render(request, 'listar_detalle_cuotas.html',
                  {'detalle_cuotas': detalles_paginados, 'pago_cu': pago_cu})

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detalles_cuota_pendiente(request, pago_cuota_id): 
    detalle_cuotas = detalle_cuotas_pendientes.objects.filter(pago_cuota_pendientes=pago_cuota_id).order_by("estado", "numero_cuota")
    pago_cu = pagos_cuotas_pendientes.objects.get(id=pago_cuota_id)
    items_por_pagina = 8
    paginator = Paginator(detalle_cuotas, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        detalles_paginados=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        detalles_paginados=paginator.get_page(1)
    return render(request, 'list_det_cuo_pen.html',
                  {'detalle_cuotas': detalles_paginados, 'pago_cu': pago_cu})


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registra_pago_cuota(request, det_cuo_id): 
    try:
        with transaction.atomic():
            detalle_cuotas = Detalle_cuotas.objects.get(id=det_cuo_id)
            cuota_actual = detalle_cuotas

            if cuota_actual.numero_cuota == 1:
                detalle_cuotas.estado = True
                pago_cuotas = Pagos_cuotas.objects.get(id=detalle_cuotas.pago_cuota.id)
                pago_cuotas.cuota_actual += 1

                if pago_cuotas.cuota_actual == pago_cuotas.numero_cuotas:
                    pago_cuotas.estado = True

                detalle_cuotas.save()
                pago_cuotas.save()

                messages.success(request, 'Se ha registrado el pago de la cuota exitosamente.')
                return redirect('/detalles_cuota/' + str(detalle_cuotas.pago_cuota.id))
            else:
                cuota_anterior = Detalle_cuotas.objects.filter(
                    fecha_descuento__lt=cuota_actual.fecha_descuento).last()

                if cuota_anterior is not None and cuota_anterior.estado:
                    detalle_cuotas.estado = True
                    pago_cuotas = Pagos_cuotas.objects.get(id=detalle_cuotas.pago_cuota.id)
                    pago_cuotas.cuota_actual += 1

                    if pago_cuotas.cuota_actual == pago_cuotas.numero_cuotas:
                        pago_cuotas.estado = True

                    detalle_cuotas.save()
                    pago_cuotas.save()

                    messages.success(request, 'Se ha registrado el pago de la cuota exitosamente.')
                    return redirect('/detalles_cuota/' + str(detalle_cuotas.pago_cuota.id))
                else:
                    messages.warning(request, 'No se puede pagar la cuota actual. La cuota del mes anterior no ha sido pagada.')
                    return redirect('/detalles_cuota/' + str(detalle_cuotas.pago_cuota.id))
    except Exception as e:
        messages.warning(request, 'Ups, ha ocurrido un problema')
    return redirect('/lista_pagos_cuotas/')

from django.db import transaction
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def eliminar_pago_cuota(request, det_cuo_id): 
    try:
        with transaction.atomic():
            pago = get_object_or_404(Pagos_cuotas, id=det_cuo_id)
            cuotas_canceladas = Detalle_cuotas.objects.filter(pago_cuota=pago, estado=True)

            if cuotas_canceladas.exists():
                messages.warning(request, 'No se puede eliminar el descuento. Hay cuotas canceladas asociadas a este pago.')
                return redirect('/lista_pagos_cuotas')
            
            pagos_cuo = Pagos_cuotas.objects.get(id=det_cuo_id)
            Detalle_cuotas.objects.filter(pago_cuota=pagos_cuo).delete()
            pagos_cuo.delete()
            messages.success(
                request, 'Se ha eliminado el pago de la cuota exitosamente.')
            return redirect('/lista_pagos_cuotas/')
    except Exception as e:
        messages.warning(request, 'Ups, ha ocurrido un problema')
    return redirect('/lista_pagos_cuotas/')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def eliminar_pago_cuota_pendiente(request, det_cuo_id):  
    try:
        with transaction.atomic():
            pago = get_object_or_404(pagos_cuotas_pendientes, id=det_cuo_id)
            cuotas_canceladas = detalle_cuotas_pendientes.objects.filter(pago_cuota_pendientes=pago, estado=True)

            if cuotas_canceladas.exists():
                messages.warning(request, 'No se puede eliminar el descuento. Hay cuotas canceladas asociadas a este pago.')
                return redirect('/lista_pagos_cuotas_pendientes')
            
            pagos_cuo = pagos_cuotas_pendientes.objects.get(id=det_cuo_id)
            detalle_cuotas_pendientes.objects.filter(pago_cuota_pendientes=pagos_cuo).delete()
            pagos_cuo.delete()
            messages.success(
                request, 'Se ha eliminado el pago de la cuota exitosamente.')
            return redirect('/lista_pagos_cuotas_pendientes/')
    except Exception as e:
        messages.warning(request, 'Ups, ha ocurrido un problema')
    return redirect('/lista_pagos_cuotas_pendientes/')


@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def agregar_pdf(request, det_id): 
    detalle_cuotas = Detalle_cuotas.objects.get(id=det_id)
    if request.method == 'GET':
        return render(request,'agregar_evidencia.html', {'detalle_cuotas': detalle_cuotas}) 
    else:
        archivo_pdf = request.FILES['evidencia']
        detalle_cuotas.evidencia=archivo_pdf
        detalle_cuotas.save()
        return redirect('/detalles_cuota/' + str(detalle_cuotas.pago_cuota.id))

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def eliminar_pago(request, pago_id):
    pagos = Pagos.objects.get(id=pago_id)
    pagos.delete()
    return redirect('/listar_pagos/')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def eliminar_pago_pendiente(request, pago_id):
    pagos = pagos_pendientes.objects.get(id=pago_id)
    pagos.delete()
    messages.success(request, 'Se ha eliminado el descuento exitosamente.')
    return redirect('/listar_pagos_pendientes/')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def extraer_datos_pdf(request):
    if request.method == 'POST':

        pdf_file = request.FILES['pdf_file']
        fs = FileSystemStorage(location=settings.MEDIA_ROOT + '/pdf')

        # file_path = fs.save('archivo.pdf', pdf_file)
        # file_path = os.path.join(settings.MEDIA_ROOT, 'pdf\\', file_path)

        tables = tabula.read_pdf(pdf_file, pages="all", encoding='latin-1', pandas_options={'header': None, 'dtype': str})
        #  tables = tabula.read_pdf(pdf_file, pages="all", encoding='latin-1', java_options=['-Xmx4G'], pandas_options={'header': None, 'dtype': str})
        datos_tabla = []

        for table in tables:
            for index, row in table.iterrows():
                row_data = {}
                datos_tabla.append(row.tolist())
        proveedores = Proveedor.objects.filter(estado=True)
        return render(request, 'extraer_descuentos.html', {'proveedores': proveedores, 'datos_tabla': datos_tabla})

    return redirect('/listar_pagos/')



def convertir_decimal(valor):
    valor = valor.replace(',', '.')
    try:
        valor_decimal = Decimal(valor)
        return   valor_decimal
    except ValueError:
        # Si no se puede convertir a decimal, devolvemos el valor original
        return valor

    
def guardar_descuentos_prov(request, id, fecha):
    
    if request.method == 'POST':
        print('entra a la funcion')
        registros_formulario = request.POST

        campos = list(registros_formulario.keys())

        campos.remove('csrfmiddlewaretoken')  # Omitir el campo del token CSRF si está presente
        # Obtener la longitud de la lista de campos
        cant_campos = len(campos)
        # Obtener la longitud de los registros (asumiendo que todos los campos tienen la misma cantidad de valores)
        cant_registros = len(registros_formulario.getlist(campos[0]))


        nombres = None
        cedulas = None
        consumos = None
        ide = registros_formulario.getlist('ide')
      
        if ide[0].isdigit():
            cedulas = registros_formulario.getlist('ide')
            
            if len(cedulas[0]) != 10:
                cedulas = None
        else:
            nombres = registros_formulario.getlist('ide')   
        des = registros_formulario.getlist('des')
        #Conversion a decimal
        consumos = [convertir_decimal(valor) for valor in des]

        for i in range(cant_registros):
            print('entro al form')
            nombre = None
            cedula = None
            consumo_total = None
            socios = None
            if cedulas != None:
                cedula = cedulas[i]
            else:
                nombre = nombres[i]
            consumo_total = consumos[i]


            if cedula != None:
                socios = Socios.objects.filter(cedula__icontains=cedula)
            elif nombre and socios is None:
                usuarios = User.objects.filter(is_staff=False)
                for usuario in usuarios:
                    if usuario.last_name + ' ' + usuario.first_name == nombre:
                        socio = usuario
                        print('usuario: ',socio)
                        
                socios = Socios.objects.filter(user_id=socio.id)
                print(usuarios)
                

            proveedor = Proveedor.objects.get(id=id)
            periodo_seleccionado = Periodo.objects.filter(activo=True).first()
            if periodo_seleccionado and periodo_seleccionado.fecha_inicio <= datetime.strptime(fecha, '%Y-%m-%d').date() <= periodo_seleccionado.fecha_fin:
                if socios.exists():
                    socio = socios.first()  # Obtener la primera instancia de Socios en la queryset socios
                    Pagos.objects.create(socio=socio, proveedor=proveedor, consumo_total=consumo_total, fecha_consumo=fecha)
                    response = {
                                                'status': True,
                                                'message': 'Registros guardados correctamente.'
                                                }
                else:
                    response = {
                                                    'status': False,
                                                    'message': 'Registros no se pudieron guardar'
                                                    }  
            else:
                    response = {
                                                    'status': False,
                                                    'message':  f'La fecha que ingresaste no esta dentro del periodo actual de {periodo_seleccionado.nombre}'
                                                    }  
    return JsonResponse(response)


def verificar_registros(request):
    if request.method == 'POST':
        registros_formulario = request.POST
        campos = list(registros_formulario.keys())
        print("registros_formulario:", registros_formulario)
        print("campos:", campos)
        campos.remove('csrfmiddlewaretoken')
        registros_con_estilo = []
        cant_registros = len(registros_formulario.getlist(campos[0]))
        cant_errores = 0
        for i in range(cant_registros):
            valor = 1
            valor1 = 1
            datos = {} 
            for campo in campos:
                datos[campo] = registros_formulario.getlist(campo)[i]  # Obtenemos el valor del campo para el registro actual
            datos['estilo_color'] = 'normal'  # Agregamos la nueva columna 'estilo_color' con valor 'normal'
            ide = registros_formulario.getlist('ide')
            if ide[i].isdigit():
                
                if Socios.objects.filter(cedula=ide[i]).exists():
                    valor=0
                    datos['estilo_color'] = 'normal'
                else:
                    cant_errores = cant_errores + 1
                    datos['estilo_color'] = 'rojo'
            else:
                usuarios = User.objects.filter(is_staff=False).order_by('first_name')
                usuario_existe = False
                for usuario in usuarios:
                    var1 = usuario.last_name + ' ' + usuario.first_name
                   
                    if var1 == ide[i]:
                        usuario_existe = True
                        break  # Romper el bucle si se encuentra una coincidencia
                
                if usuario_existe:
                    valor = 0
                else:
                    valor = 1
             
            des = registros_formulario.getlist('des')
            des[i] = des[i].replace(',', '').replace('.', '')
            if des[i].isdigit():
                valor1 = 0
                # print('es digito')
            else:
                cant_errores = cant_errores + 1
            # print(des[i])
            #cambio color
            if valor == 0 and valor1 == 0:
                datos['estilo_color'] = 'normal'
            else:
                cant_errores = cant_errores + 1
                datos['estilo_color'] = 'rojo'
            registros_con_estilo.append(datos)

        # print(registros_con_estilo)
        # print(valor,'  ',valor1)
        # print(cant_errores)
        # proveedores = Proveedor.objects.filter(estado=True)
        if cant_errores > 0:
            response = {
                'status': False,
                'message': 'Se han encontrado errores en los registros. Por favor, verifíquelos.',
                'registros': registros_con_estilo  # Agrega los registros con estilo a la respuesta
            }
        else:
            response = {
                'status': True,
                'message': 'No se han encontrado errores en los registros',
                'registros': registros_con_estilo  # Agrega los registros con estilo a la respuesta
            }

        #return redirect(request, 'extraer_descuentos.html', {'proveedores': proveedores, 'datos_tabla': registros_con_estilo})
    return JsonResponse(response)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def generar_reporte_pdf(request):
    fecha_actual_str = request.POST.get('fecharpcmp')
    fecha_actual = datetime.strptime(fecha_actual_str, '%Y-%m-%d')
    mes = fecha_actual.month
    anio = fecha_actual.year

    # Llamar al procedimiento almacenado en la base de datos y pasarle los parámetros
    with connection.cursor() as cursor:
        cursor.execute('CALL obtener_consumo_proveedores(%s, %s)', [mes, anio])

    # Obtener los datos del reporte desde la tabla temporal creada por el procedimiento almacenado
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM consumo_proveedores')
        datos_reporte = cursor.fetchall()


    # Obtener los proveedores para la cabecera de la tabla en el reporte
    proveedores = Proveedor.objects.all().order_by('nombre')

    image_path = os.path.join(os.path.dirname(__file__), 'static', 'img', 'aduteq.png')
    fecha_gen=datetime.now()

    # Renderizar el template HTML utilizando el contexto
    template = get_template('reporte_proveedores.html')
    context = {
        'mes': mes,
        'anio': anio,
        'proveedores': proveedores,
        'datos_reporte': datos_reporte,
        'image_path': image_path,
        'fecha_gen': fecha_gen
    }
    html = template.render(context)

    # Crear un objeto PDF utilizando xhtml2pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_consumo_proveedores_{mes}_{anio}.pdf"'

    buffer = BytesIO()
   
    pisa.showLogging()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), buffer, pagesize=landscape((14*inch, 8.5*inch)))

    if not pdf.err:
        response.write(buffer.getvalue())
        buffer.close()
        return response

    buffer.close()
    return HttpResponse("Error al generar el PDF", status=500)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def convertir_cuotas(request, pago_id):
    if request.method == 'GET':
        pagos = Pagos.objects.get(id=pago_id)
        # form = PagosForm(instance=pagos)
        print(pagos.consumo_total)
        return render(request, 'convertir_cuotas.html', {'pagos': pagos})
    else:
            socio_id = request.POST.get('socio')
            socios = Socios.objects.get(id=socio_id)

            proveedor_id = request.POST.get('proveedor')
            proveedores = Proveedor.objects.get(id=proveedor_id)

            cantidad = request.POST.get('consumo_total')
            numero_cuota = request.POST.get('numero_cuotas')

            fecha_descuento = str(request.POST.get('fecha_descuento'))
            fecha_actual = datetime.strptime(fecha_descuento, "%Y-%m-%d")
                
            if fecha_actual.day < 15:
                fecha_inicio_pagos = fecha_actual.replace(day=15)
            else:
                next_month = fecha_actual.replace(day=1) + timedelta(days=32)
                fecha_inicio_pagos = next_month.replace(day=15)
                
            cantidadval = float(cantidad)
            n_cuota = float(numero_cuota)
            valor_cuo = cantidadval / n_cuota

            periodo_seleccionado = Periodo.objects.filter(activo=True).first()
            if periodo_seleccionado and periodo_seleccionado.fecha_inicio <= datetime.strptime(fecha_descuento, '%Y-%m-%d').date() <= periodo_seleccionado.fecha_fin:
                pagoscuotas = Pagos_cuotas.objects.create(
                    socio=socios, proveedor=proveedores, consumo_total=cantidad, fecha_descuento=fecha_descuento,
                    numero_cuotas=numero_cuota, cuota_actual=0, valor_cuota=valor_cuo
                )
                pagoscuotas.save()

                fechas_pago = [fecha_inicio_pagos + timedelta(days=(30 * i)) for i in range(int(numero_cuota))]
                    
                for numero_cuota, fecha_pago in enumerate(fechas_pago, start=1):
                        detalle_cuotas = Detalle_cuotas(
                            pago_cuota=pagoscuotas,
                            numero_cuota=numero_cuota,
                            fecha_descuento=fecha_pago,
                            valor_cuota=valor_cuo,
                            socio=socios, proveedor=proveedores
                        )
                        detalle_cuotas.save()

                pagox = request.POST.get('id_pago')
                print(pagox)
                eliminar_pago(request,pagox)

                messages.success(request, 'Se ha agregado con exito el descuento por cuotas')
                return redirect('/lista_pagos_cuotas/')
            else:
                    messages.warning(request, f'La fecha que ingresaste no está dentro del período actual de {periodo_seleccionado.nombre}')
                    users = User.objects.filter(is_active=True)
                    socios = Socios.objects.filter(user__in=users)
                    proveedores = Proveedor.objects.filter(estado=True)
                    return render(request, 'agregar_pago_cuotas.html', {'socios': socios, 'proveedores': proveedores})


def buscar_pagos(request):
    if request.method == "POST":
        criterio = request.POST.get('criterio')
        valor = request.POST.get('query')
        pagos = []

        if criterio:
            # Realiza las consultas según el criterio y el valor ingresados
            if criterio == 'nombres':
                pagos = Pagos.objects.filter(socio__user__first_name__icontains=valor) | Pagos.objects.filter(socio__user__last_name__icontains=valor)
            elif criterio == 'proveedor':
                pagos = Pagos.objects.filter(proveedor__nombre__icontains=valor)
            elif criterio == 'fecha':
                pagos = Pagos.objects.filter(fecha_consumo__icontains=valor)
            elif criterio == '1':
                pagos = Pagos.objects.filter(estado=True)
            elif criterio == '0':
                pagos = Pagos.objects.filter(estado=False)

        items_por_pagina = 10  # Cambia esto según tus necesidades
        paginator = Paginator(pagos, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            pagos_paginados = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            pagos_paginados = paginator.get_page(1)

        # Renderiza una tabla parcial con los resultados
        rendered_table = render_to_string("lista_pagos_partial.html", {"pagos": pagos_paginados})

        return JsonResponse({"rendered_table": rendered_table})

    return JsonResponse({"error": "Método no permitido"}, status=400)

def buscar_pagos_pendientes(request):
    if request.method == "POST":
        criterio = request.POST.get('criterio')
        valor = request.POST.get('query')
        pagos = []

        if criterio:
            # Realiza las consultas según el criterio y el valor ingresados
            if criterio == 'nombres':
                pagos = pagos_pendientes.objects.filter(socio__user__first_name__icontains=valor) | pagos_pendientes.objects.filter(socio__user__last_name__icontains=valor)
            elif criterio == 'proveedor':
                pagos = pagos_pendientes.objects.filter(proveedor__nombre__icontains=valor)
            elif criterio == 'fecha':
                pagos = pagos_pendientes.objects.filter(fecha_consumo__icontains=valor)
            elif criterio == '1':
                pagos = pagos_pendientes.objects.filter(estado=True)
            elif criterio == '0':
                pagos = pagos_pendientes.objects.filter(estado=False)

        items_por_pagina = 10  # Cambia esto según tus necesidades
        paginator = Paginator(pagos, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            pagos_paginados = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            pagos_paginados = paginator.get_page(1)

        # Renderiza una tabla parcial con los resultados
        rendered_table = render_to_string("list_pag_pen_par.html", {"pagos": pagos_paginados})

        return JsonResponse({"rendered_table": rendered_table})

    return JsonResponse({"error": "Método no permitido"}, status=400)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def agregar_pagos_cuotas_pen(request):
    try:
        with transaction.atomic():
            if request.method == 'GET':
                users = User.objects.filter(is_active=True)
                socios = Socios.objects.filter(user__in=users)
                proveedores = Proveedor.objects.filter(estado=True)
                return render(request, 'agregar_pago_cuo_pen.html', {'socios': socios, 'proveedores': proveedores})
            else:
                socio_id = request.POST.get('socio')
                socios = Socios.objects.get(id=socio_id)

                # proveedor_id = request.POST.get('proveedor')
                # proveedores = Proveedor.objects.get(id=proveedor_id)

                cantidad = request.POST.get('consumo_total')
                numero_cuota = request.POST.get('numero_cuotas')

                fecha_descuento = str(request.POST.get('fecha_descuento'))
                fecha_actual = datetime.strptime(fecha_descuento, "%Y-%m-%d")
                
                if fecha_actual.day < 15:
                    fecha_inicio_pagos = fecha_actual.replace(day=15)
                else:
                    next_month = fecha_actual.replace(day=1) + timedelta(days=32)
                    fecha_inicio_pagos = next_month.replace(day=15)
                
                cantidadval = float(cantidad)
                n_cuota = float(numero_cuota)
                valor_cuo = cantidadval / n_cuota 

                periodo_seleccionado = Periodo.objects.filter(activo=True).first()
                if periodo_seleccionado and periodo_seleccionado.fecha_inicio <= datetime.strptime(fecha_descuento, '%Y-%m-%d').date() <= periodo_seleccionado.fecha_fin:
                    pagoscuotas = pagos_cuotas_pendientes.objects.create(
                        socio=socios, consumo_total=cantidad, fecha_descuento=fecha_descuento,
                        numero_cuotas=numero_cuota, cuota_actual=0, valor_cuota=valor_cuo
                    )
                    pagoscuotas.save()

                    fechas_pago = [fecha_inicio_pagos + timedelta(days=(30 * i)) for i in range(int(numero_cuota))]
                    
                    for numero_cuota, fecha_pago in enumerate(fechas_pago, start=1):
                        detalle_cuotas = detalle_cuotas_pendientes(
                            pago_cuota_pendientes=pagoscuotas,
                            numero_cuota=numero_cuota,
                            fecha_descuento=fecha_pago,
                            valor_cuota=valor_cuo,
                            socio=socios
                        )
                        detalle_cuotas.save()

                    messages.success(request, 'Se ha agregado con éxito el descuento por cuotas')
                    return redirect('/lista_pagos_cuotas_pendientes/')
                else:
                    messages.warning(request, f'La fecha que ingresaste no está dentro del período actual de {periodo_seleccionado.nombre}')
                    users = User.objects.filter(is_active=True)
                    socios = Socios.objects.filter(user__in=users)
                    proveedores = Proveedor.objects.filter(estado=True)
                    return render(request, 'agregar_pago_cuo_pen.html', {'socios': socios, 'proveedores': proveedores})
            
    except Exception as e:
        messages.warning(request, 'Ups, ha ocurrido un problema, verifica los valores ingresados')
    return redirect('/lista_pagos_cuotas_pendientes/')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def lista_pagos_cuotas_pendientes(request):
    periodos = Periodo.objects.all()  # Obtener todos los períodos
    anos = periodos.values_list('anio', flat=True).distinct()
    #listar periodo por el select
    periodoid = request.POST.get('periodoid')
    fechas_periodo = {}
    if periodoid:
        periodo_seleccionado = Periodo.objects.filter(id=periodoid).first()
        print(periodo_seleccionado)
        if periodo_seleccionado:
            fechas_periodo = {
                'fecha_inicio': periodo_seleccionado.fecha_inicio,
                'fecha_fin': periodo_seleccionado.fecha_fin
            }
           
            print(periodo_seleccionado)
            pagos = pagos_cuotas_pendientes.objects.filter(
                Q(fecha_descuento__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])) |
                Q(fecha_descuento__lt=fechas_periodo['fecha_inicio'], estado="False")
            ).order_by("-id","estado")
    
            context = {
                'pago_cuotas': pagos,
                'periodos': periodos,
                'anos': anos,
                'fechas_periodo': fechas_periodo,
                'periodo_seleccionado': periodo_seleccionado,
            }
            rendered_table = render_to_string("pagos_cuotas_partial.html",context)
            return JsonResponse({"rendered_table": rendered_table})
    
    #listar periodo actual
    periodo_seleccionado = Periodo.objects.filter(activo=True).first()
    if periodo_seleccionado:
        fechas_periodo = {
            'fecha_inicio': periodo_seleccionado.fecha_inicio,
            'fecha_fin': periodo_seleccionado.fecha_fin
        }
        pagos = pagos_cuotas_pendientes.objects.filter(
                Q(fecha_descuento__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])) |
                Q(fecha_descuento__lt=fechas_periodo['fecha_inicio'], estado="False")
            ).order_by("-id","estado")
        items_por_pagina = 10
        paginator = Paginator(pagos, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            pagos = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            pagos = paginator.get_page(1)
    else:
        pagos = {}
    context = {
        'pago_cuotas': pagos,
        'periodos': periodos,
        'anos': anos,
        'fechas_periodo': fechas_periodo,
        'periodo_seleccionado': periodo_seleccionado,
    }
    return render(request, 'pagos_cuotas_pendientes.html', context)

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registra_pago_cuota_pen(request, det_cuo_id): 
    try:
        with transaction.atomic():
            detalle_cuotas = detalle_cuotas_pendientes.objects.get(id=det_cuo_id)
            cuota_actual = detalle_cuotas.numero_cuota

            if cuota_actual == 1:
                detalle_cuotas.estado = True
                pago_cuotas = pagos_cuotas_pendientes.objects.get(id=detalle_cuotas.pago_cuota_pendientes.id)
                pago_cuotas.cuota_actual += 1

                if pago_cuotas.cuota_actual == pago_cuotas.numero_cuotas:
                    pago_cuotas.estado = True

                detalle_cuotas.save()
                pago_cuotas.save()

                messages.success(request, 'Se ha registrado el pago de la cuota exitosamente.')
                return redirect('/detalles_cuota_pendiente/' + str(detalle_cuotas.pago_cuota_pendientes.id))
            else:
                cuota_anterior = detalle_cuotas_pendientes.objects.filter(
                    fecha_descuento__lt=detalle_cuotas.fecha_descuento,
                    pago_cuota_pendientes=detalle_cuotas.pago_cuota_pendientes,
                    numero_cuota=cuota_actual - 1
                ).first()

                if cuota_anterior is not None and cuota_anterior.estado:
                    detalle_cuotas.estado = True
                    pago_cuotas = pagos_cuotas_pendientes.objects.get(id=detalle_cuotas.pago_cuota_pendientes.id)
                    pago_cuotas.cuota_actual += 1

                    if pago_cuotas.cuota_actual == pago_cuotas.numero_cuotas:
                        pago_cuotas.estado = True

                    detalle_cuotas.save()
                    pago_cuotas.save()

                    messages.success(request, 'Se ha registrado el pago de la cuota exitosamente.')
                    return redirect('/detalles_cuota_pendiente/' + str(detalle_cuotas.pago_cuota_pendientes.id))
                else:
                    messages.warning(request, 'No se puede pagar la cuota actual. La cuota del mes anterior no ha sido pagada.')
                    return redirect('/detalles_cuota_pendiente/' + str(detalle_cuotas.pago_cuota_pendientes.id))
    except Exception as e:
        messages.warning(request, 'Ups, ha ocurrido un problema')
        return redirect('/lista_pagos_cuotas_pendientes/')

@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def agregar_pdf2(request, det_id): 
    detalle_cuotas = detalle_cuotas_pendientes.objects.get(id=det_id)
    if request.method == 'GET':
        return render(request,'agregar_evidencia2.html', {'detalle_cuotas': detalle_cuotas}) 
    else:
        archivo_pdf = request.FILES['evidencia']
        detalle_cuotas.evidencia=archivo_pdf
        detalle_cuotas.save()
        return redirect('/detalles_cuota_pendiente/' + str(detalle_cuotas.pago_cuota_pendientes.id))
    
@login_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def convertir_cuotas2(request, pago_id):
    if request.method == 'GET':
        try:
            pagos = pagos_pendientes.objects.get(id=pago_id)
            # form = PagosForm(instance=pagos)
            print(pagos.consumo_total)
            return render(request, 'convertir_pendientes.html', {'pagos': pagos})
        except Exception as e:
            messages.warning(request, 'Ups, ha ocurrido un problema')
            return redirect('/lista_pagos_cuotas_pendientes/')

    else:
            socio_id = request.POST.get('socio')
            socios = Socios.objects.get(id=socio_id)

            # proveedor_id = request.POST.get('proveedor')
            # proveedores = Proveedor.objects.get(id=proveedor_id)

            cantidad = request.POST.get('consumo_total')
            numero_cuota = request.POST.get('numero_cuotas')

            fecha_descuento = str(request.POST.get('fecha_descuento'))
            fecha_actual = datetime.strptime(fecha_descuento, "%Y-%m-%d")
                
            if fecha_actual.day < 15:
                fecha_inicio_pagos = fecha_actual.replace(day=15)
            else:
                next_month = fecha_actual.replace(day=1) + timedelta(days=32)
                fecha_inicio_pagos = next_month.replace(day=15)
                
            cantidadval = float(cantidad)
            n_cuota = float(numero_cuota)
            valor_cuo = cantidadval / n_cuota

            periodo_seleccionado = Periodo.objects.filter(activo=True).first()
            if periodo_seleccionado and periodo_seleccionado.fecha_inicio <= datetime.strptime(fecha_descuento, '%Y-%m-%d').date() <= periodo_seleccionado.fecha_fin:
                pagoscuotas = pagos_cuotas_pendientes.objects.create(
                    socio=socios, consumo_total=cantidad, fecha_descuento=fecha_descuento,
                    numero_cuotas=numero_cuota, cuota_actual=0, valor_cuota=valor_cuo
                )
                pagoscuotas.save()

                fechas_pago = [fecha_inicio_pagos + timedelta(days=(30 * i)) for i in range(int(numero_cuota))]
                    
                for numero_cuota, fecha_pago in enumerate(fechas_pago, start=1):
                        detalle_cuotas = detalle_cuotas_pendientes(
                            pago_cuota_pendientes=pagoscuotas,
                            numero_cuota=numero_cuota,
                            fecha_descuento=fecha_pago,
                            valor_cuota=valor_cuo,
                            socio=socios
                        )
                        detalle_cuotas.save()

                pagox = request.POST.get('id_pago')
                print(pagox)
                eliminar_pago_pendiente(request,pagox)

                messages.success(request, 'Se ha agregado con exito el descuento por cuotas')
                return redirect('/lista_pagos_cuotas_pendientes/')
            else:
                    messages.warning(request, f'La fecha que ingresaste no está dentro del período actual de {periodo_seleccionado.nombre}')
                    users = User.objects.filter(is_active=True)
                    socios = Socios.objects.filter(user__in=users)
                    proveedores = Proveedor.objects.filter(estado=True)
                    return render(request, 'agregar_pago_cuotas.html', {'socios': socios, 'proveedores': proveedores})