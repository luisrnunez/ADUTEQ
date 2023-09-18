from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . import models
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from django.http import JsonResponse
from django.core.paginator import Paginator, PageNotAnInteger
from django.shortcuts import get_object_or_404
from socios.models import Socios
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, Page
from proveedores.models import Proveedor
import os
from PIL import Image
from django.template.loader import render_to_string
from io import BytesIO
from email.mime.image import MIMEImage
import smtplib
from html import unescape
from bs4 import BeautifulSoup

# Create your views here.
@login_required
def ListaPromociones(request):
    promociones = models.Promocion.objects.all().order_by('estado')

    for promocion in promociones:
        promocion.contiene_tabla = contiene_tabla(promocion.descripcion)

    items_por_pagina = 10
    paginator = Paginator(promociones, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
        promociones_pag = paginator.get_page(numero_pagina)
    except PageNotAnInteger:
        promociones_pag = paginator.get_page(1)
    return render(request, "promociones.html", {'promociones': promociones_pag})

@login_required
def habilitar_desabilitar_promocion(request, promo_id, valor):
    promocion = models.Promocion.objects.get(id=promo_id)

    if request.method == 'GET':
        # Cambiar el estado de la promocion a inactivo
        print(valor)
        if valor == 0:
            promocion.estado = True
            promocion.save()
            messages.success(
                request, 'La promoción se habilitó correctamente.')
        else:
            promocion.estado = False
            promocion.save()
            messages.success(
                request, 'La promocion se desabilitó correctamente.')

        # Agregar un mensaje de confirmación

    else:
        messages.warning(request, 'Ups, algo salío mal')

    return redirect('/promociones/')


def formRegistro(request):
    proveedores=models.Proveedor.objects.all()

    return render(request,'agg_promocion.html', {'proveedores':proveedores})

@login_required
def aggPromo(request):
    if request.method == 'POST':
        tipo=request.POST.get('selectipo')
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        if 'imagen' in request.FILES:
            imagen = request.FILES.get('imagen')
        else:
            imagen=None
        if 'fecha_inicio' in request.POST:
            fecha_inicio = request.POST.get('fecha_inicio')
        else:
            fecha_inicio=None

        if 'fecha_fin'in request.POST:
            fecha_fin = request.POST.get('fecha_fin')
        else:
            fecha_fin=None
        estado = request.POST.get('estado')

        if 'proveedor' in request.POST:
            proveedor_id = request.POST.get('proveedor')
        else:
            proveedor_id=None

        if 'evidencia' in request.FILES:
            evidenciaa = request.FILES['evidencia']
        else:
            evidenciaa=None

        if userexist(titulo):
            response = {
                'status': 'error',
                'message': 'Ya existe una promoción registrada con este título'
            }
        else:
            promocion = models.Promocion(
                tipo=tipo,
                titulo=titulo,
                descripcion=descripcion,
                imagen=imagen,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado=estado,
                proveedor_id=proveedor_id,
                evidencia=evidenciaa
            )
            promocion.save()

            response = {
                'status': 'success',
                'message': 'Promo agregada con éxito'
            }
        
        return JsonResponse(response)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})




#Metodos verificar si existe o no proveedor
def userexist(titulo):
    try:
        promocion = models.Promocion.objects.get(titulo=titulo)
        return True
    except models.Promocion.DoesNotExist:
        return False
    

@login_required
def editar_promo(request, promo_id):
    promocion = models.Promocion.objects.get(id=promo_id)
    promocion.descripcion=unescape(promocion.descripcion)
    proveedores=models.Proveedor.objects.all()
    if request.method == 'POST':
        #try:
           
            if 'imagen' in request.FILES:
                promocion.imagen = request.FILES['imagen']
            
            if 'evidencia' in request.FILES:
                promocion.evidencia=request.FILES['evidencia']
              
            promocion.titulo = request.POST.get('titulo')
            if 'proveedor' in request.POST and request.POST['proveedor']:
                proveedor_id = request.POST['proveedor']
                promocion.proveedor = get_object_or_404(models.Proveedor, id=proveedor_id)
            else:
                promocion.proveedor = None
            promocion.tipo=request.POST.get('tipo')
            promocion.descripcion=request.POST.get('descripcion')
            promocion.fecha_inicio = request.POST.get('fecha_inicio')
            promocion.fecha_fin = request.POST.get('fecha_fin')
            promocion.estado = request.POST.get('estado')

            
            if models.Promocion.objects.exclude(id=request.POST.get('id')).filter(titulo=request.POST.get('titulo')).exists():
                response = {
                    'status': 'error',
                    'message': 'Ya existe una promoción registrada con este título'
                }
            else:
                promocion.save()
                response = {
                    'status': 'success',
                    'message': 'Promoción editada correctamente'
                }
            return JsonResponse(response)
    else:
        return render(request, 'edit_promocion.html', {'promocion':promocion, 'proveedores':proveedores})
    
def eliminarpromo(request, promo_id):
    promocion=models.Promocion.objects.get(id=promo_id)
    if request.method == 'POST':
        promocion.delete()
        response = {'status': 'success', 'message': 'Promoción eliminada correctamente'}
    else:
        response = {'status': 'error', 'message': 'Método no permitido'}

    return JsonResponse(response)


# def enviar_promocion_a_todos(request, promo_id):
#     socios = Socios.objects.filter(user__is_active=True)
#     promocion = models.Promocion.objects.get(id=promo_id)

#     try:
#         for socio in socios:
#             template = get_template('correo_promo.html')
#             contexto = {'promocion': promocion}
#             contenido = template.render(contexto)

#             emisor_personalizado = 'williamvera210@gmail.com'
#             if(promocion.tipo):
#                 asunto='Nueva Promoción'
#             else:
#                 asunto='Nuevo Comunicado'

#             email = EmailMultiAlternatives(
#                 asunto+': ' + promocion.titulo,
#                 'Nueva promoción disponible',
#                 settings.EMAIL_HOST_USER,
#                 [socio.user.email])

#             email.attach_alternative(contenido, 'text/html')

#             if promocion.imagen:
#                 # Redimensionar la imagen manteniendo la relación de aspecto
#                 maximo_ancho = 800  # Puedes ajustar esto según tus necesidades
#                 imagen_original = Image.open(promocion.imagen.path)
                
#                 if imagen_original.mode == 'RGBA':
#                     imagen_original = imagen_original.convert('RGB')
                
#                 ancho_original, alto_original = imagen_original.size
#                 nuevo_ancho = min(ancho_original, maximo_ancho)
#                 nuevo_alto = int(nuevo_ancho * (alto_original / ancho_original))
#                 imagen_redimensionada = imagen_original.resize((nuevo_ancho, nuevo_alto))

#                 imagen_io = BytesIO()
#                 imagen_redimensionada.save(imagen_io, format='JPEG')


#                 imagen_adjunta = MIMEImage(imagen_io.getvalue())
#                 nombre_imagen=promocion.imagen
#                 imagen_adjunta.add_header('Content-ID', '<promocion_imagen>')
#                 imagen_adjunta.add_header('Content-Disposition', f'inline; filename="{nombre_imagen}"')
#                 email.attach(imagen_adjunta)

#             # Verificamos si hay un PDF adjunto
#             if promocion.evidencia:
#                 nombrepdf = os.path.basename(promocion.evidencia.path) 


#                 with open(promocion.evidencia.path, 'rb') as archivo_pdf:
#                     email.attach('Comunicado.pdf', archivo_pdf.read(), 'application/pdf')

#             email.send()

#         respuesta = {'status': 'success', 'message': 'Promoción enviada a todos los socios'}
#     except Exception as e:
#         respuesta = {'status': 'error', 'message': str(e)}

#     return JsonResponse(respuesta)

def enviar_promocion_a_todos(request, promo_id):
    socios = Socios.objects.filter(user__is_active=True)
    promocion = models.Promocion.objects.get(id=promo_id)
    respuesta = {}

    try:
        template = get_template('correo_promo.html')
        contexto = {'promocion': promocion}
        contenido = template.render(contexto)

        emisor_personalizado = 'williamvera210@gmail.com'
        if promocion.tipo:
            asunto = 'Nueva Promoción'
        else:
            asunto = '¡AVISO!'

        # Lista de correos electrónicos de muestra (reemplaza con tus correos)
        lista_correos = [socio.user.email for socio in socios]

        tamano_bloque = 25
        bloques = [lista_correos[i:i + tamano_bloque] for i in range(0, len(lista_correos), tamano_bloque)]

        for bloque in bloques:
            email = EmailMultiAlternatives(
                asunto + ': ' + promocion.titulo,
                'Nueva promoción disponible',
                settings.EMAIL_HOST_USER,
                bloque  # Envía el bloque actual como destinatarios
            )

            email.attach_alternative(contenido, 'text/html')

            if promocion.imagen:
                # Redimensionar la imagen manteniendo la relación de aspecto
                maximo_ancho = 800  # Puedes ajustar esto según tus necesidades
                imagen_original = Image.open(promocion.imagen.path)

                if imagen_original.mode == 'RGBA':
                    imagen_original = imagen_original.convert('RGB')

                ancho_original, alto_original = imagen_original.size
                nuevo_ancho = min(ancho_original, maximo_ancho)
                nuevo_alto = int(nuevo_ancho * (alto_original / ancho_original))
                imagen_redimensionada = imagen_original.resize((nuevo_ancho, nuevo_alto))

                imagen_io = BytesIO()
                imagen_redimensionada.save(imagen_io, format='JPEG')

                imagen_adjunta = MIMEImage(imagen_io.getvalue())
                nombre_imagen = promocion.imagen.name  # Usar el nombre del archivo
                imagen_adjunta.add_header('Content-ID', '<promocion_imagen>')
                imagen_adjunta.add_header('Content-Disposition', f'inline; filename="{nombre_imagen}"')
                email.attach(imagen_adjunta)

            # Verificamos si hay un PDF adjunto
            if promocion.evidencia:
                nombrepdf = os.path.basename(promocion.evidencia.name)  # Usar el nombre del archivo

                with open(promocion.evidencia.path, 'rb') as archivo_pdf:
                    email.attach(nombrepdf, archivo_pdf.read(), 'application/pdf')

            email.send()

        respuesta = {'status': 'success', 'message': 'Promoción enviada a todos los socios'}

    except Exception as e:
        respuesta = {'status': 'error', 'message': str(e)}

    return JsonResponse(respuesta)


def buscar_promo(request):
    if request.method == "POST":
        criterio = request.POST.get('criterio')
        valor = request.POST.get('query')
        promos = []
        print(valor,criterio)
        if criterio:
            # Filtrar socios según el criterio y el valor ingresados
            if criterio == 'titulo':
                promos = models.Promocion.objects.filter(titulo__icontains=valor)
  
        rendered_table = render_to_string("tabla_parcialpromos.html", {"promos": promos})
        
        return JsonResponse({"rendered_table": rendered_table})

    return JsonResponse({"error": "Método no permitido"}, status=400)


def obtener_resultados(request):
    seleccion = request.GET.get('seleccion')
    page_number = request.GET.get('page', 1)

    if seleccion == 'promociones':
        resultados = models.Promocion.objects.filter(tipo=True)
    elif seleccion == 'comunicados':
        resultados = models.Promocion.objects.filter(tipo=False)
    else:
        resultados = []

    paginator = Paginator(resultados, 10)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        page = Page([])

    return render(request, 'promociones.html', {'page': page, 'seleccion': seleccion})

def buscar_proveedores(request):
    query = request.GET.get('query', '')  # Obtiene el texto de búsqueda
    proveedores_sugeridos = []

    if query:
        # Realiza la búsqueda de proveedores en la base de datos
        proveedores_sugeridos = Proveedor.objects.filter(nombre__icontains=query)[:10]

    sugerencias = [{'id': proveedor.id, 'nombre': proveedor.nombre} for proveedor in proveedores_sugeridos]
    return JsonResponse({'sugerencias': sugerencias})

def contiene_tabla(descripcion):
    soup = BeautifulSoup(descripcion, 'html.parser')
    tablas = soup.find_all('table')
    return len(tablas) > 0
