import datetime
import re
import datetime
import re
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from . import models
from socios.models import Socios
from django.utils import timezone
from django.contrib.auth.models import User
from django.views import View
from socios.models import Socios
from django.utils import timezone
from django.contrib.auth.models import User
from . import models
from django.core.paginator import Paginator, PageNotAnInteger

# Create your views here.

def login_(request):
    return render(request, "login.html")

def is_superuser_or_staff(user):
    return user.is_superuser or user.is_staff

class SinAccesoView(View):
    def get(self, request):
        mensaje = "Lo siento, no tienes acceso."
        return render(request, 'login.html', {'mensaje': mensaje})

@login_required
def cerrar_sesion(request):
    logout(request)
    return render(request, 'login.html')


@login_required
def cerrar_sesion(request):
    logout(request)
    return render(request, 'login.html')


@login_required
def Principal(request):
    return render(request, "base.html")


@login_required
def PanelActividades(request):
    return render(request, "emp_actividades.html")


def Autenticacion_usuarios(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        print(username, password, user)
        if user is not None:
            login(request, user)
            # redirige a la página de inicio después del inicio de sesión exitoso
            return redirect('principal')
        else:
           
            return render(request, 'login.html',{'error_message': 'Usuario o contraseña incorrecto, porfavor ingrese de nuevo'})
    else:
        return render(request, 'login.html')



@login_required
def guardar_socio(request):


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        cedula = request.POST.get('cedula')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        lugar_nacimiento = request.POST.get('lugar_nacimiento')
        email = request.POST.get('email')
        numero_telefonico = request.POST.get('numero_telefonico')
        numero_convencional = request.POST.get('numero_convencional')
        direccion_domiciliaria = request.POST.get('direccion_domiciliaria')
        facultad = request.POST.get('facultad')
        categoria = request.POST.get('categoria')
        dedicacion_academica = request.POST.get('dedicacion_academica')
        titulo = request.POST.get('titulo')
        aporte = request.POST.get('aporte')
        foto = request.POST.get('foto')

        user = User(username=username,password=password, email=email, first_name=first_name, last_name=last_name)
                             
        if User.objects.filter(username=username).exists():
                messages.warning(
                    request, 'El nombre de usuario ya está registrado')
                return render(request, 'emp_agg_socios.html', {'socio': request.POST,'user': user})
        if Socios.objects.filter(cedula=cedula).exists():
                messages.warning(
                    request, 'El número de cédula ya está registrado')
                return render(request, 'emp_agg_socios.html', {'socio': request.POST,'user': user})
        if User.objects.filter(email=email).exists():
                messages.warning(
                    request, 'El correo ya está registrado, ingrese otro')
                return render(request, 'emp_agg_socios.html', {'socio': request.POST,'user': user})
        if Socios.objects.filter(numero_telefonico=numero_telefonico).exists():
                messages.warning(
                    request, 'El número de telefono ya está registrado')
                return render(request, 'emp_agg_socios.html', {'socio': request.POST,'user': user})
        if Socios.objects.filter(numero_convencional=numero_convencional).exists():
                messages.warning(
                    request, 'El número de convencional ya está registrado')
                return render(request, 'emp_agg_socios.html', {'socio': request.POST,'user': user})

        user = User.objects.create_user(username=username,password=password, email=email,
                              last_login=timezone.now().date(),
                              is_superuser=False, first_name=first_name, last_name=last_name,
                              is_staff=False, is_active=True, date_joined=timezone.now().date())
        
        socios = Socios(user=user,cedula=cedula, fecha_nacimiento=fecha_nacimiento,lugar_nacimiento=lugar_nacimiento,
                            numero_telefonico=numero_telefonico,numero_convencional=numero_convencional, direccion_domiciliaria=direccion_domiciliaria,
                            categoria=categoria,facultad=facultad,
                            dedicacion_academica=dedicacion_academica,aporte=aporte,
                            titulo=titulo,foto=foto)
      
            
        socios.save()
        messages.success(request, 'Se ha agregado un nuevo socio')

        # Redirigir a la página deseada después de guardar los datos
        return redirect('listar_socios')
   
    return render(request, 'emp_socios.html')

@login_required
def editar_socio(request, socio_id):
    socio = Socios.objects.get(id=socio_id)
    usuario = User.objects.get(id=socio.user_id)
    if request.method == 'POST':
        #try:
           
            if 'foto' in request.FILES:
                socio.foto = request.FILES['foto']
              
            usuario.username = request.POST.get('username')
            usuario.set_password(request.POST['password'])
            socio.cedula = request.POST.get('cedula')
            usuario.first_name = request.POST.get('first_name')
            usuario.last_name = request.POST.get('last_name')
            socio.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            socio.lugar_nacimiento = request.POST.get('lugar_nacimiento')
            usuario.email = request.POST.get('email')
            socio.numero_telefonico = request.POST.get('numero_telefonico')
            socio.numero_convencional = request.POST.get('numero_convencional')
            socio.direccion_domiciliaria = request.POST.get(
                'direccion_domiciliaria')
            socio.facultad = request.POST.get('facultad')
            socio.categoria = request.POST.get('categoria')
            socio.dedicacion_academica = request.POST.get(
                'dedicacion_academica')
            socio.titulo = request.POST.get('titulo')
            socio.aporte = request.POST.get('aporte')

            if User.objects.exclude(id=usuario.id).filter(username=usuario.username).exists():
                messages.warning(request, 'El nombre de usuario ya está registrado')
                return render(request, 'emp_edit_socios.html', {'socio': socio})
            if Socios.objects.exclude(id=socio_id).filter(cedula=socio.cedula).exists():
                messages.warning(request, 'El número de cédula ya está registrado')
                return render(request, 'emp_edit_socios.html', {'socio': socio})
            if User.objects.exclude(id=usuario.id).filter(email=usuario.email).exists():
                messages.warning(request, 'El correo ya está registrado')
                return render(request, 'emp_edit_socios.html', {'socio': socio})
            if Socios.objects.exclude(id=socio_id).filter(numero_telefonico=socio.numero_telefonico).exists():
                messages.warning(request, 'El número de telefono ya está registrado')
                return render(request, 'emp_edit_socios.html', {'socio': socio})


            usuario.save()
            socio.save()

            messages.success(
                request, 'Se ha guardado correctamente este socio')
            return redirect('listar_socios')
        #except:
            #messages.warning(request, 'Error de integridad en los datos')
            #return redirect('listar_socios')
    else:
        return render(request, 'emp_edit_socios.html', {'socio': socio})


@login_required
def eliminar_socio(request, user_id, valor):
    socio = Socios.objects.get(id=user_id)

    if request.method == 'GET':
        # Cambiar el estado del socio a inactivo
        print(valor)
        if valor == 0:
            socio.is_active = True
            socio.user.is_active=True
            socio.save()
            socio.user.save()
            messages.success(
                request, 'El socio se habilitado exitosamente.')
        else:
            socio.is_active = False
            socio.user.is_active=False
            socio.save()
            socio.user.save()
            messages.success(
                request, 'El socio ha sido dado de baja exitosamente.')

        # Agregar un mensaje de confirmación

    else:
        messages.warning(request, 'El socio no pudo ser eliminado')

    return redirect('listar_socios')


def buscar_socios(request):

    criterio = request.GET.get('criterio')
    valor = request.GET.get('valor')
    socios = []

    if criterio:
        # Filtrar socios según el criterio y el valor ingresados
        if criterio == 'nombres':
            users = User.objects.filter(first_name__icontains=valor)
            socios = Socios.objects.filter(user__in=users)
            users = User.objects.filter(socio__in=socios)
        elif criterio == 'apellidos':
            users = User.objects.filter(last_name__icontains=valor)
            socios = Socios.objects.filter(user__in=users)
            users = User.objects.filter(socio__in=socios)
        elif criterio == 'categoria':
            socios = Socios.objects.filter(categoria__icontains=valor)
            users = User.objects.filter(socio__in=socios)
        elif criterio == 'facultad':
            socios = Socios.objects.filter(facultad__icontains=valor)
            users = User.objects.filter(socio__in=socios)
        elif criterio == 'cedula':
            socios = Socios.objects.filter(cedula__icontains=valor)
            users = User.objects.filter(socio__in=socios)
        elif criterio == '1':
            users = User.objects.filter(is_active=True)
            socios = Socios.objects.filter(user__in=users)
            users = User.objects.filter(socio__in=socios)
        elif criterio == '0':
            users = User.objects.filter(is_active=False)
            socios = Socios.objects.filter(user__in=users)
            users = User.objects.filter(socio__in=socios)

    return render(request, 'emp_socios.html', {'users': users})


def Recuperar_cuenta(request):
    return render(request, "recuperar_contra.html")


@login_required
def ListaSocios(request):
    socios = Socios.objects.all().order_by('user')
    items_por_pagina = 8
    paginator = Paginator(socios, items_por_pagina)
    numero_pagina = request.GET.get('page')
    try:
         socios_pag=paginator.get_page(numero_pagina)
    except PageNotAnInteger:
         socios_pag=paginator.get_page(1)
    return render(request, "emp_socios.html", {'socios': socios_pag})


def AggSocio(request):
    return render(request, "emp_agg_socios.html")
