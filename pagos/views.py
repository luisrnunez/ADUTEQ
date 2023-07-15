import datetime
import os
import re
import PyPDF2
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Socios, Proveedor, Pagos
from .forms import PagosForm
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import datetime
import tabula
from django.contrib import messages


# Create your views here.
def lista_pagos(request):
    pagos = Pagos.objects.all()
    return render(request, 'listar_pagos.html', {'pagos': pagos})


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

        # Procesar cada tabla extraída
        for table in tables:
            # Obtener los encabezados de la tabla
            headers = table.columns.tolist()

            # Recorrer las filas de la tabla
            for index, row in table.iterrows():
                # Obtener los valores de cada columna en la fila
                column = row.tolist()
                row_data = {}
                row_data['cedula'] = column[0] if len(column) >= 1 else ''
                row_data['nombre'] = column[1] if len(column) >= 2 else ''
                row_data['consumo_total'] = column[2] if len(
                    column) >= 3 else ''
                datos_tabla.append(row_data)

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
        print('cantidad de registros:', cant_registros)
        print('cantidad de campos:', cant_campos)
        if cant_campos == 3 :
            #validando que el primer campo se ha cedula
            nombres = None
            cedulas = None
            consumos = None
            campo1 = registros_formulario.getlist(campos[0])
            if campo1[0].isdigit():
                cedulas = registros_formulario.getlist(campos[0])
                if len(cedulas[0]) != 10:
                    cedulas = None
            #Validando si el segundo campo es nombre 
            nombres = registros_formulario.getlist(campos[1])
            campo3 = registros_formulario.getlist(campos[2])
            if campo3[0].isdigit():
                consumos = registros_formulario.getlist(campos[2])

            for i in range(cant_registros):
                if cedulas != None:
                    cedula = cedulas[i]
                nombre = nombres[i]
                consumo_total = consumos[i]
                
                print('cedula:', cedula)
                print('nombre:', nombre)
                print('consumo_total:', consumo_total)
                
                if cedula != None:
                    socios = Socios.objects.filter(cedula__icontains=cedula)
                elif nombre and socios is None:
                    users = User.objects.filter(first_name__icontains=nombre)
                    socios = Socios.objects.filter(user__in=users)
                proveedor = Proveedor.objects.get(id=id)
                if socios.exists():
                    socio = socios.first()  # Obtener la primera instancia de Socios en la queryset socios
                    Pagos.objects.create(socio=socio, proveedor=proveedor, consumo_total=consumo_total, fecha_consumo=fecha)
                    response = {
                                    'status': 'success',
                                    'message': 'Registros guardados correctamente.'
                                    }
    return JsonResponse(response)
