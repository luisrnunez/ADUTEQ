import datetime
from gettext import translation
import os
import re
import PyPDF2
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Socios, Proveedor, Pagos, Pagos_cuotas, Detalle_cuotas
from .forms import PagosForm
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import datetime, timedelta
import tabula
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger


# Create your views here. 
def lista_pagos(request):
    pagos = Pagos.objects.all().order_by("-fecha_consumo", "proveedor")
    items_por_pagina = 8
    paginator = Paginator(pagos, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        pagos=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        pagos=paginator.get_page(1)
    return render(request, 'listar_pagos.html', {'pagos': pagos})


def lista_pagos_cuotas(request):
    pago_cuotas = Pagos_cuotas.objects.all().order_by("estado")
    items_por_pagina = 8
    paginator = Paginator(pago_cuotas, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        pagos_paginados=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        pagos_paginados=paginator.get_page(1)
    return render(request, 'pagos_cuotas.html', {'pago_cuotas': pagos_paginados})


def extraer_descuentos(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'extraer_descuentos.html', {'proveedores': proveedores})


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

        cantidad = request.POST.get('consumo_total')
        fecha = request.POST.get('fecha_consumo')

        pagos = Pagos.objects.create(
            socio=socios, proveedor=proveedores, consumo_total=cantidad, fecha_consumo=fecha)

        return redirect('/listar_pagos/')


def agregar_pagos_cuotas(request):
    try:
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
            # fecha = request.POST.get('fecha_descuento')
            numero_cuoa = request.POST.get('numero_cuotas')

            fecha = str(request.POST.get('fecha_descuento'))
            fecha_actual = datetime.strptime(fecha, "%Y-%m-%d")
            fechas_pago = [
                fecha_actual + timedelta(days=(30 * (i+1))) for i in range(int(numero_cuoa))]

            cantidadval = float(cantidad)
            n_cuota = float(numero_cuoa)
            valor_cuo = cantidadval / n_cuota

            pagoscuotas = Pagos_cuotas.objects.create(
                socio=socios, proveedor=proveedores, consumo_total=cantidad, fecha_descuento=fecha,
                numero_cuotas=numero_cuoa, cuota_actual=0, valor_cuota=valor_cuo
            )
            pagoscuotas.save()

            for numero_cuota, fecha_pago in enumerate(fechas_pago, start=1):
                detalle_cuatas = Detalle_cuotas(
                    pago_cuota=pagoscuotas,
                    numero_cuota=numero_cuota,
                    fecha_descuento=fecha_pago
                )
                detalle_cuatas.save()

            return redirect('/lista_pagos_cuotas/')
    except Exception as e:
        messages.success(request, 'Ups, ha ocurrido un problema, verifica los valores ingresados')
    return redirect('/lista_pagos_cuotas/')


def editar_pago(request, pago_id):
    if request.method == 'GET':
        pagos = Pagos.objects.get(id=pago_id)
        form = PagosForm(instance=pagos)
        return render(request, 'editar_pago.html', {'pagos': pagos, 'form': form})
    else:
        pagos = Pagos.objects.get(id=pago_id)
        pagos.consumo_total = request.POST.get('consumo_total')
        pagos.fecha_consumo = request.POST.get('fecha_consumo')
        pagos.save()
        return redirect('/listar_pagos/')


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


def registra_pago_cuota(request, det_cuo_id):
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


def eliminar_pago_cuota(request, det_cuo_id):
    # try:
    #     with translation.atomic():
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
    # except Exception as e:
    #     messages.success(request, 'Ups, ha ocurrido un problema')
    # return redirect('/lista_pagos_cuotas/')



def agregar_pdf(request, det_id): 
    detalle_cuotas = Detalle_cuotas.objects.get(id=det_id)
    if request.method == 'GET':
        return render(request,'agregar_evidencia.html', {'detalle_cuotas': detalle_cuotas}) 
    else:
        archivo_pdf = request.FILES['evidencia']
        detalle_cuotas.evidencia=archivo_pdf
        detalle_cuotas.save()
        return redirect('/detalles_cuota/' + str(detalle_cuotas.pago_cuota.id))

def eliminar_pago(request, pago_id):
    pagos = Pagos.objects.get(id=pago_id)
    pagos.delete()
    return redirect('/listar_pagos/')


def extraer_datos_pdf(request):
    if request.method == 'POST':

        pdf_file = request.FILES['pdf_file']
        # Configurar el almacenamiento del archivo en la carpeta "media" del proyecto
        fs = FileSystemStorage(location=settings.MEDIA_ROOT + '/pdf')

        # Guardar el archivo PDF en la carpeta "pdf" dentro de la carpeta "media"
        file_path = fs.save('archivo.pdf', pdf_file)
        file_path = os.path.join(settings.MEDIA_ROOT, 'pdf\\', file_path)

        tables = tabula.read_pdf(pdf_file, pages="all")

     

        datos_tabla = []

        # print(tables)

        # Procesar cada tabla extraída
        for table in tables:
            # Obtener los encabezados de la tabla
            #headers = table.columns.tolist()
            #print(headers)

            # Recorrer las filas de la tabla
            for index, row in table.iterrows():
                # Obtener los valores de cada columna en la fila
                #column = row.tolist()
                row_data = {}
                # print(row.tolist())
                #row_data['cedula'] = column[0] if len(column) >= 1 else ''
                #row_data['nombre'] = column[1] if len(column) >= 2 else ''
                #row_data['consumo_total'] = column[2] if len(
                #    column) >= 3 else ''
                datos_tabla.append(row.tolist())

        proveedores = Proveedor.objects.filter(estado=True)
        return render(request, 'extraer_descuentos.html', {'proveedores': proveedores, 'datos_tabla': datos_tabla})

    return redirect('/listar_pagos/')


def guardar_descuentos_prov(request, id, fecha):
    if request.method == 'POST':

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
        print(ide)
        if ide[0].isdigit():
            cedulas = registros_formulario.getlist('ide')
            if len(cedulas[0]) != 10:
                cedulas = None
        else:
            nombres = registros_formulario.getlist('ide')   
        des = registros_formulario.getlist('des')
        if des[0].isdigit():
            consumos = registros_formulario.getlist('des')



        for i in range(cant_registros):
            nombre = None
            cedula = None
            consumo_total = None
            socios = None
            if cedulas != None:
                cedula = cedulas[i]
            else:
                nombre = nombres[i]
            consumo_total = consumos[i]
            print(nombre)
            print(consumo_total)

            if cedula != None:
                socios = Socios.objects.filter(cedula__icontains=cedula)
            elif nombre and socios is None:
                users = User.objects.filter(first_name__icontains=nombre)
                socios = Socios.objects.filter(user__in=users)
                print(socios)
            proveedor = Proveedor.objects.get(id=id)
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
    return JsonResponse(response)

def verificar_registros(request):
    if request.method == 'POST':
        registros_formulario = request.POST

        campos = list(registros_formulario.keys())
        campos.remove('csrfmiddlewaretoken')
        registros_con_estilo = []
        cant_registros = len(registros_formulario.getlist(campos[0]))
        valor = 0
        for i in range(cant_registros):
            datos = {} 
            for campo in campos:
                datos[campo] = registros_formulario.getlist(campo)[i]  # Obtenemos el valor del campo para el registro actual
            datos['estilo_color'] = 'normal'  # Agregamos la nueva columna 'estilo_color' con valor 'normal'
            
            ide = registros_formulario.getlist('ide')
            if ide[i].isdigit():
                if Socios.objects.filter(cedula__icontains=ide[i]).exists():
                    datos['estilo_color'] = 'normal'
                else:
                    valor=1
                    datos['estilo_color'] = 'rojo'
            else:
                if User.objects.filter(first_name__icontains=ide[i]).exists():
                    datos['estilo_color'] = 'normal'
                    print('existe de usuario')
                else:
                    valor=1
                    datos['estilo_color'] = 'rojo'
                    print(' no existe de usuario')
            registros_con_estilo.append(datos)
        print(registros_con_estilo)
        proveedores = Proveedor.objects.filter(estado=True)
        if valor == 1:
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
