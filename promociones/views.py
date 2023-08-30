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
import os
from PIL import Image
from django.template.loader import render_to_string
from io import BytesIO

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib

# Create your views here.
@login_required
def ListaPromociones(request):
    promociones=models.Promocion.objects.all().order_by('estado')
    
    items_por_pagina = 10
    paginator = Paginator(promociones, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
         promociones_pag=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
         promociones_pag=paginator.get_page(1)
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
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')  # Usar FILES en mayúsculas
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        estado = request.POST.get('estado')
        proveedor_id = request.POST.get('proveedor')

        if userexist(titulo):
            response = {
                'status': 'error',
                'message': 'Ya existe una promoción registrada con este título'
            }
        else:
            promocion = models.Promocion(
                titulo=titulo,
                descripcion=descripcion,
                imagen=imagen,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                estado=estado,
                proveedor_id=proveedor_id
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
    proveedores=models.Proveedor.objects.all()
    if request.method == 'POST':
        #try:
           
            if 'imagen' in request.FILES:
                promocion.imagen = request.FILES['imagen']
              
            promocion.titulo = request.POST.get('titulo')
            proveedor_id = request.POST.get('proveedor')
            promocion.proveedor = get_object_or_404(models.Proveedor, id=proveedor_id)
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


def enviar_promocion_a_todos(request, promo_id):
    socios = Socios.objects.filter(user__is_active=True)
    promocion = models.Promocion.objects.get(id=promo_id)
    
    try:
        for socio in socios:
            template = get_template('correo_promo.html')
            context = {'promocion': promocion}
            content = template.render(context)

            emisor_personalizado = 'williamvera210@gmail.com'
            
            emaill = EmailMultiAlternatives(
                'Nueva Promoción: ' + promocion.titulo,
                'Nueva promoción disponible',
                settings.EMAIL_HOST_USER,
                [socio.user.email])
            
            # agregamos el contenido HTML
            emaill.attach_alternative(content, 'text/html')
            
            # redimensionar la imagen y convertirla a formato JPEG
            imagen = Image.open(promocion.imagen)
            imagen = imagen.convert("RGB")  # convertir a modo RGB
            imagen = imagen.resize((800, 600))  # cambia las dimensiones
            imagen_io = BytesIO()
            imagen.save(imagen_io, format='JPEG')
            
            # agregamos la imagen redimensionada al correo
            imagen_adjunta = MIMEImage(imagen_io.getvalue())
            imagen_adjunta.add_header('Content-ID', '<promocion_imagen>')
            emaill.attach(imagen_adjunta)
            
            emaill.send()
            
        response = {'status': 'success', 'message': 'Promoción enviada a todos los socios'}
    except Exception as e:
        response = {'status': 'error', 'message': str(e)}
    
    return JsonResponse(response)

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
