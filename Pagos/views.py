import datetime
from decimal import Decimal
from gettext import translation
import os
import re
import PyPDF2
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Socios, Proveedor, Pagos, Pagos_cuotas, Detalle_cuotas
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



# Create your views here. 
def lista_pagos(request):
    pagos = Pagos.objects.all().order_by("-fecha_consumo", "proveedor")
    items_por_pagina = 10
    paginator = Paginator(pagos, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        pagos=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        pagos=paginator.get_page(1)
    return render(request, 'listar_pagos.html', {'pagos': pagos})


def lista_pagos_cuotas(request):
    pago_cuotas = Pagos_cuotas.objects.all().order_by("estado")
    items_por_pagina = 10
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
        cupo=detallesCupos.objects.get(proveedor=proveedores,socio=socios)
        fecha = request.POST.get('fecha_consumo')
        cantidad = request.POST.get('consumo_total')
        if(float(cantidad)<=cupo.cupo):
            pagos = Pagos.objects.create(socio=socios, proveedor=proveedores, consumo_total=cantidad, fecha_consumo=fecha)
            messages.success(request, 'Exito')
            return redirect('/listar_pagos/')
        else:
            messages.warning(request, 'La cantidad que desea ingresar es superior a la brindada por el proveedor')
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

            # if(str(cantidad)>cupo):
            #     messages.warning(request, 'El valor que desea ingrear es superior al cupo brindado por el proveedor')

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

            messages.success(request, 'Se ha agregado con exito el descuento por cuotas')
            return redirect('/lista_pagos_cuotas/')
    except Exception as e:
        messages.warning(request, 'Ups, ha ocurrido un problema, verifica los valores ingresados')
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
                    if usuario.first_name + ' ' + usuario.last_name == nombre:
                        socio = usuario
                        print('usuario: ',socio)
                        
                socios = Socios.objects.filter(user_id=socio.id)
                print(usuarios)
                

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
                    datos['estilo_color'] = 'normal'
                else:
                    valor=0
                    datos['estilo_color'] = 'rojo'
            else:
                usuarios = User.objects.filter(is_staff=False)
                usuario_existe = False
                for usuario in usuarios:
                    if usuario.first_name + ' ' + usuario.last_name == ide[i]:
                        usuario_existe = True
                        break
                if usuario_existe:
                    valor = 0
                registros_con_estilo.append(datos)
            des = registros_formulario.getlist('des')
            des[i] = des[i].replace(',', '').replace('.', '')
            if des[i].isdigit():
                valor1 = 0
                print('es digito')
            print(des[i])
            #cambio color
            if valor == 0 and valor1 == 0:
                datos['estilo_color'] = 'normal'
            else:
                datos['estilo_color'] = 'rojo'

        print(registros_con_estilo)
        proveedores = Proveedor.objects.filter(estado=True)
        if valor == 0 and valor1 == 0:
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


def generar_reporte_pdf(request):
    mes = 7
    anio = 2023

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

    # Crear un objeto PDF utilizando ReportLab
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="reporte_{mes}_{anio}.pdf"'

    # Inicializar el documento PDF
    PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)

    # Inicializar el documento PDF con tamaño de página apaisada
    doc = SimpleDocTemplate(response, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    # Crear una lista con los datos del reporte
    data = [['Nombre Socio'] + [proveedor.nombre for proveedor in proveedores]]
    data.extend([row for row in datos_reporte])


    # Crear una tabla con los datos y aplicar estilos
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0x62/255, 0xc5/255, 0x62/255)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)

    # Ajustar el ancho de las columnas automáticamente
    table._argW[0] = 140  # Ancho de la primera columna (Nombre Socio)
    for i in range(1, len(proveedores) + 1):
        table._argW[i] = doc.width / (len(proveedores) + 1)


    # Agregar la tabla al documento PDF
    story = []
    img_width = 100
    img_height = 100
    img = Image(image_path, width=img_width, height=img_height)
    story.append(img)
    story.append(table)
    doc.build(story)

    return response
