from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import AyudasMot,AyudasEconomicas, Socios, DetallesAyuda,ConsumosCuotaOrdinaria
from django.core.paginator import Paginator, PageNotAnInteger
from django.contrib import messages
from .models import datos_para_ayuda
from django.db import transaction
from .models import Periodo, AyudasExternas
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.db.models import Q
from decimal import Decimal

# Create your views here.
def motivos(request):
    
    motivos = AyudasMot.objects.all()
    items_por_pagina = 10
    paginator = Paginator(motivos, items_por_pagina)
    numero_pagina = request.GET.get('page')
    
    try:
        motivos_pag = paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        motivos_pag = paginator.get_page(1)
    
  
    contexto = {
        'motivos': motivos_pag,
        'periodo': {} ,

    }
    
    return render(request, 'motivoayuda.html', contexto)

#metodo para agregar nuevos motivos
def formRegistro(request):
    return render(request,'aggmotivo.html')

def aggMotivo(request):
    motivo=AyudasMot(motivo=request.POST['motivo'], descripcion=request.POST['descripcion'])

    if(userexist(request.POST['motivo'])):
        response = {
                'status': 'error',
                'message': 'Ya existe un motivo registrado con este nombre'
            }
    else:
        motivo.save()
        response = {
            'status': 'success',
            'message': 'Motivo registrado correctamente.'
            }
    return JsonResponse(response)


#Metodos verificar si existe o no proveedor
def userexist(motivo):
    try:
        motivo = AyudasMot.objects.get(motivo=motivo)
        return True
    except AyudasMot.DoesNotExist:
        return False

#metodos editar proveedores
def feditMotivo(request, codigo):
    motivos=AyudasMot.objects.get(id=codigo)
    return render(request,'editmotivo.html',{
        'motivos': motivos
    })

def editarmotivo(request):
    motivop=request.POST.get('motivo')
    descripcionp=request.POST.get('descripcion')
    evidenciap=request.POST.get('evidencia')
    motivoo= get_object_or_404(AyudasMot, id=request.POST.get('id'))

    if AyudasMot.objects.exclude(id=request.POST.get('id')).filter(motivo=motivop).exists():
        response = {
            'status': 'error',
            'message': 'Ya existe un motivo registrado con este nombre'

          }
    else:
        motivoo.motivo=motivop
        motivoo.descripcion=descripcionp
        # motivoo.evidencia=evidenciap
        motivoo.save()
        response = {
            'status': 'success',
            'message': 'Datos actualizados correctamente'
            }

    return JsonResponse(response)

#metodo para eliminar un motivo.
def deleteMotivo(request, codigo):
    motivo=AyudasMot.objects.get(id=codigo)
    motivo.delete()
    return redirect('/motivos')


#--------------------------------------------------------------------
#-----------------------------Ayudas economicas----------------------
# def mostrar_opciones(request):
#     opciones = Socios.objects.all()
#     return render(request, 'aggAyuda.html', {'opciones': opciones})

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def viewayudas(request):
    periodos = Periodo.objects.all()  # Obtener todos los períodos
    anos = periodos.values_list('anio', flat=True).distinct()
    total_ayuda_permanente, total_cuota_ordinaria=datos_para_ayuda()
    periodoid = request.POST.get('periodoid')
    fechas_periodo = {}
    
    if periodoid:
        periodo_seleccionado = Periodo.objects.filter(id=periodoid).first()
        if periodo_seleccionado:
            fechas_periodo = {
                'fecha_inicio': periodo_seleccionado.fecha_inicio,
                'fecha_fin': periodo_seleccionado.fecha_fin
            }
            
            ayudas = AyudasEconomicas.objects.filter(fecha__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])).order_by("socio","fecha")
            
            # Configura la paginación
            items_por_pagina = 10  # Número de elementos por página
            paginator = Paginator(ayudas, items_por_pagina)
            page = request.GET.get('page')  # Obtén el número de página de la solicitud GET
            
            try:
                ayudas_paginadas = paginator.page(page)
            except PageNotAnInteger:
                # Si el número de página no es un entero, muestra la primera página
                ayudas_paginadas = paginator.page(1)
            except EmptyPage:
                # Si el número de página está fuera de rango, muestra la última página
                ayudas_paginadas = paginator.page(paginator.num_pages)
            
            context = {
                'ayudas': ayudas_paginadas,
                'periodos': periodos,
                'anos': anos,
                'fechas_periodo': fechas_periodo,
                'periodo_seleccionado': periodo_seleccionado,
                'total_ayuda_permanente':total_ayuda_permanente,
                'total_cuota_ordinaria':total_cuota_ordinaria
            }
            
            # Renderiza la tabla parcial con la paginación
            rendered_table = render_to_string("ayudasecon_partial.html", context)
            
            # Devuelve la tabla parcial paginada como respuesta JSON
            return JsonResponse({"rendered_table": rendered_table})

    
    #listar periodo actual
    periodo_seleccionado = Periodo.objects.filter(activo=True).first()
    if periodo_seleccionado:
        fechas_periodo = {
            'fecha_inicio': periodo_seleccionado.fecha_inicio,
            'fecha_fin': periodo_seleccionado.fecha_fin
        }
        ayudas = AyudasEconomicas.objects.filter(fecha__range=(fechas_periodo['fecha_inicio'], fechas_periodo['fecha_fin'])).order_by("socio","fecha")
    else:
        ayudas = {}
    context = {
        'ayudas': ayudas,
        'periodos': periodos,
        'anos': anos,
        'fechas_periodo': fechas_periodo,
        'periodo_seleccionado': periodo_seleccionado,
        'total_ayuda_permanente':total_ayuda_permanente,
        'total_cuota_ordinaria':total_cuota_ordinaria
    }
    return render(request, 'ayudasecon.html', context)

    # ayudas=AyudasEconomicas.objects.all()
    # return render(request,'ayudasecon.html', {
    #     'ayudas': ayudas
    # })

def formRegistroAyuda(request):
    opciones = Socios.objects.select_related('user').all()
    motivos=AyudasMot.objects.all()
    total_ayuda_permanente, total_cuota_ordinaria=datos_para_ayuda()
    return render(request,'aggAyuda.html',{
        'opciones':opciones, 'motivos':motivos, 'total_ayuda_permanente':total_ayuda_permanente,
        'total_cuota_ordinaria':total_cuota_ordinaria
    })

def aggAyuda(request):
    mmotivo=AyudasMot.objects.get(id=request.POST.get('motivo'))
    socios_disponibles=Socios.objects.all()
    total_ayuda_permanente, total_cuota_ordinaria=datos_para_ayuda()
    print(total_ayuda_permanente)
    valorsocio = 0
    
    if 'valorsocio' in request.POST:
        valorsocio_input = request.POST.get('valorsocio')
        if valorsocio_input != '':
            valorsocio = Decimal(valorsocio_input)
    if(request.POST.get('socio')=="null"):
        ayuda=AyudasEconomicas(socio=None, descripcion=request.POST['descripcion'], evidencia=None, valorsocio=valorsocio ,total = Decimal(request.POST['total']), motivo=mmotivo, fecha=request.POST['fecha'])
    else:
        socio=Socios.objects.get(id=request.POST['socio'])
        ayuda=AyudasEconomicas(socio=socio, descripcion=request.POST['descripcion'], evidencia=None, valorsocio=valorsocio, total = Decimal(request.POST['total']), motivo=mmotivo, fecha=request.POST['fecha'])

    if ayuda.total <= total_ayuda_permanente[0][1]:
        # Utiliza una transacción para evitar crear detalles de ayuda si ocurre un error
        with transaction.atomic():
            try:
                ayuda.save()
                for Socio in socios_disponibles:
                    if Socio.user.is_active:
                        DetallesAyuda.objects.create(
                            fecha=None,
                            ayuda=ayuda,
                            socio=Socio,
                            valor=ayuda.valorsocio,
                            cancelado=False
                        )
                
                response = {
                    'status': 'success',
                    'message': 'Ayuda agregada correctamente.'
                }
            except Exception as e:
                response = {
                    'status': 'error',
                    'message': 'Ha existido algún error: {}'.format(str(e))
                }
    else:
        response = {
            'status': 'error',
            'message': 'El total es mayor que el valor permitido.'
        }
    
    return JsonResponse(response)


#metodos editar ayudas
def feditAyuda(request, codigo):
    opciones = Socios.objects.all()
    motivos=AyudasMot.objects.all()
    ayuda=AyudasEconomicas.objects.get(id=codigo)
    return render(request,'editarayuda.html',{
        'ayuda': ayuda, 'socios': opciones, 'motivos':motivos
    })

def detallesAyuda(request, ayuda_id):
    ayuda=AyudasEconomicas.objects.get(id=ayuda_id)
    detalleAyuda=DetallesAyuda.objects.filter(ayuda=ayuda).order_by("cancelado")
    items_por_pagina = 10
    paginator = Paginator(detalleAyuda, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        detalles_paginados=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        detalles_paginados=paginator.get_page(1)
    return render(request, 'detalles_ayuda.html',{'detalles': detalles_paginados, 'detalle_id':ayuda_id})


def registro_ayuda(request, detalle_id, valor):
    detalleayuda=get_object_or_404(DetallesAyuda, id=detalle_id)
    if(valor==0):
        detalleayuda.cancelado=True
        detalleayuda.fecha=date.today()
        detalleayuda.save()
        messages.success(request, 'Registro agregado exitosamente')
    else:
        messages.success(request, 'Ups, ocurrio un error en la transaccion')
    return redirect('/detalleayuda/'+str(detalleayuda.ayuda.id))

def presagregar_pdf2(request, det_id): 
    registro_pago = DetallesAyuda.objects.get(id=det_id)
    if request.method == 'GET':
        return render(request,'editar_detalles_prestamo.html', {'pago_men': registro_pago}) 
    else:
        archivo_pdf = request.FILES['evidencia']
        registro_pago.evidencia=archivo_pdf
        registro_pago.save()
        return redirect('/detalleayuda/' + str(registro_pago.ayuda.id))
    
def eliminar_ayuda(request, codigo):
    try:
        with transaction.atomic():

            ayuda = get_object_or_404(AyudasEconomicas, id=codigo)
            detalles = DetallesAyuda.objects.filter(ayuda=ayuda, cancelado=True)
            if detalles.exists():
                messages.warning(request, 'No se puede eliminar la ayuda. Hay registros de aportaciones asociadas a esta ayuda.')
                return redirect('/verayudas')

            # Obtenemos el préstamo
            ayuda2 = AyudasEconomicas.objects.get(id=codigo)

            # Eliminamos todas las cuotas del préstamo
            DetallesAyuda.objects.filter(ayuda=ayuda2).delete()

            # Eliminamos el préstamo
            ayuda2.delete()
            messages.success(request,'La ayuda fue eliminada de manera exitosa!!')

    except Exception as e:
        # Si ocurre algún error durante la transacción, la transacción se revierte automáticamente
        messages.warning(request,'Ups, ha ocurrido un problema')
    return redirect('/verayudas')

from django.http import JsonResponse

def guardar_aportacion(request, detalle_id):
    if request.method == 'POST':
        detalleayuda = get_object_or_404(DetallesAyuda, id=detalle_id)
        valor = request.POST.get('valor')
        print(valor)
        
        if valor is not None:
            detalleayuda.cancelado=True
            detalleayuda.fecha=date.today()
            detalleayuda.valor = valor
            detalleayuda.save()
            return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})

# def verificar_socio(request, detalle_id):
#     detalle = DetallesAyuda.objects.get(id=detalle_id)
#     socio_id_null = detalle.ayuda.socio_id is None
#     return JsonResponse({'socio_id_null': socio_id_null})

def buscar_detalle(request, ayuda_id):
    if request.method == "POST":
        criterio = request.POST.get('criterio')
        valor = request.POST.get('query')
        detalles_ayuda = DetallesAyuda.objects.filter(ayuda=ayuda_id).order_by("cancelado")

        if criterio:
            if criterio == 'nombres':
                detalles_ayuda = detalles_ayuda.filter(
                    Q(socio__user__first_name__icontains=valor) | Q(socio__user__last_name__icontains=valor)
                )
            elif criterio == 'apellidos':
                detalles_ayuda = detalles_ayuda.filter(
                    Q(socio__user__first_name__icontains=valor) | Q(socio__user__last_name__icontains=valor))

        items_por_pagina = 10
        paginator = Paginator(detalles_ayuda, items_por_pagina)
        numero_pagina = request.GET.get('page')
        try:
            detalles_paginados = paginator.get_page(numero_pagina)
        except PageNotAnInteger:
            detalles_paginados = paginator.get_page(1)

        rendered_table = render_to_string("tabla_detalles.html", {"detalles": detalles_paginados})

        return JsonResponse({"rendered_table": rendered_table})

    return JsonResponse({"error": "Método no permitido"}, status=400)

def registrar_aportacion_externa(request, detalle_id):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_aportador')
        cedula = request.POST.get('cedula_aportador')
        valor = request.POST.get('valor1')
        print(valor)
        fecha = request.POST.get('fecha')
        detalle_id = request.POST.get('detalle_id')  # Asegúrate de agregar un campo oculto en tu formulario HTML para el detalle_id
        detallea=AyudasEconomicas.objects.get(id=detalle_id)
        
            
        # Guardar la aportación externa en la base de datos
        aportacion_externa = AyudasExternas(
            nombre=nombre,
            cedula=cedula,
            fecha=fecha,
            detalle=detallea,
            valor=valor
        )
        aportacion_externa.save()
            
        # Puedes retornar una respuesta JSON si lo deseas
        response_data = {'message': 'Aportación externa registrada con éxito'}
    return JsonResponse(response_data)

def obtener_ayudas_externas(request, detalle_id):
    detalle = AyudasEconomicas.objects.get(id=detalle_id)
    ayudas_externas = AyudasExternas.objects.filter(detalle=detalle)
        
    return render(request, 'ayudas_externas.html', {'ayudas_externas': ayudas_externas, 'detalle_id':detalle.id})

def editar_evidencia_ayuda(request, ayuda_id):
    ayuda= AyudasEconomicas.objects.get(id=ayuda_id)
    if request.method=='GET':
        return render(request,'editar_evidencia_ayuda.html', {'ayuda': ayuda })
    else:
        if 'evidencia' in request.FILES:
            ayuda.evidencia=request.FILES['evidencia']
        else:
            messages.warning(request, "Seleccione un archivo en formato pdf")
        messages.success(request,'La evidencia fue editada de manera exitosa')
        ayuda.save()

        return redirect('/verayudas/')


#------------------------------------Cuotas Ordinarias--------------------------------------#
def listar_gastos_cuotas_ordinaria(request):
    total_ayuda_permanente, total_cuota_ordinaria=datos_para_ayuda()
    gastos=ConsumosCuotaOrdinaria.objects.all().order_by('-fecha')
    items_por_pagina = 10
    paginator = Paginator(gastos, items_por_pagina)
    numero_pagina = request.GET.get('page')
    
    try:
        gastos_pag = paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        gastos_pag = paginator.get_page(1)
    
  
    contexto = {
        'gastos': gastos_pag,
        'periodo': {} ,
        'total_ayuda_permanente':total_ayuda_permanente,
        'total_cuota_ordinaria':total_cuota_ordinaria

    }
    
    return render(request, 'consumos_cuota_ordinaria.html', contexto)

def registrar_consumo_ordinaria(request):
    total_ayuda_permanente, total_cuota_ordinaria = datos_para_ayuda()
    
    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        valor = Decimal(request.POST.get('consumo'))  # Convertir el valor a Decimal
        fecha = request.POST.get('fecha')
        
        if 'evidencia' in request.FILES:
            evidencia = request.FILES['evidencia']
        else:
            evidencia = None
        
        # Verificar si el valor es menor o igual a total_cuota_ordinaria
        if valor <= total_cuota_ordinaria[0][1]:
            # Guardar el consumo en la base de datos
            consumo_cuota = ConsumosCuotaOrdinaria(
                descripcion=descripcion,
                valor=valor,
                fecha=fecha,
                evidencia=evidencia,
            )
            consumo_cuota.save()
            response_data = {'message': 'Consumo registrado con éxito'}
        else:
            response_data = {'status': 'error', 'message': 'El valor del consumo es mayor que la cuota ordinaria disponible.'}
    
    return JsonResponse(response_data)

def editar_evidencia_consumo(request, consumo_id):
    consumo= ConsumosCuotaOrdinaria.objects.get(id=consumo_id)
    if request.method=='GET':
        return render(request,'editar_evidencia_ordinaria.html', {'consumo': consumo })
    else:
        if 'evidencia' in request.FILES:
            consumo.evidencia=request.FILES['evidencia']
        else:
            messages.warning(request, "Seleccione un archivo en formato pdf")
        messages.success(request,'La evidencia fue editada de manera exitosa')
        consumo.save()

        return redirect('/lista_cuotas_ordinarias/')
    
def deleteConsumo(request, consumo_id):
    consumo=ConsumosCuotaOrdinaria.objects.get(id=consumo_id)
    consumo.delete()
    return redirect('/lista_cuotas_ordinarias')