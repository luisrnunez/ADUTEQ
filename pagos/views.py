import datetime
import os
from django.conf import settings
from django.shortcuts import render, redirect
from .models import Socios, Proveedor, Pagos
from .forms import PagosForm
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from datetime import datetime



# Create your views here.
def lista_pagos(request):
    pagos = Pagos.objects.all()
    return render(request, 'listar_pagos.html', {'pagos': pagos})


def agrefar_pagos(request):
    if request.method == 'GET':
        socios = Socios.objects.select_related('user').all()
        proveedores = Proveedor.objects.all()
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

        print(file_path)
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            # Leer el contenido del PDF
            content = ''
            page_num = 0
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                content += page.extract_text()

                lineas = content.split('\n')
                proveedor = None
                fecha = None
                datos_socios = []
                for linea in lineas:
                        if linea.startswith('Proveedor:'):
                            proveedor = linea.split(':')[1].strip()
                            print(proveedor)
                        elif linea.startswith('Fecha:'):
                            fecha_str = linea.split(':')[1].strip()
                            fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
                            print(fecha)
                        elif linea.startswith('Cédula'):
                            continue  # Saltar la línea de encabezados
                        else:
                            datos = linea.split('\t')
                            if len(datos) >= 3:
                                cedula = datos[0].strip() 
                                nombre = datos[1].strip()
                                consumo_total = float(datos[2].replace('$', '').replace(',', ''))
                                print(cedula + ' ' + nombre + ' ' + consumo_total)
                                print(cedula)
                                datos_socios.append({'cedula': cedula, 'nombre': nombre, 'consumo_total': consumo_total})
            # Guardar los datos en la base de datos

                print(datos_socios)
                proveedor_obj = Proveedor.objects.get(nombre=proveedor)
                for datos_socio in datos_socios:
                        socio_obj = Socios.objects.get(cedula=datos_socio['cedula'], nombre=datos_socio['nombre'])
                        Pagos.objects.create(socio=socio_obj, proveedor=proveedor_obj, consumo_total=datos_socio['consumo_total'], fecha=fecha)
                 

    return redirect('/listar_pagos/')
